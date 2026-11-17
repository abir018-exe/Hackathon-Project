import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update
from uuid import UUID
import structlog

from app.core.config import settings
from app.db.session import Base
from app.models import Project, ScanSession, ScanFinding, SecretFinding, ScanStatus, IssueType, IssueCategory, RiskLevel, Feature, FeatureType, FeatureStatus

logger = structlog.get_logger()

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript (React)",
    ".tsx": "TypeScript (React)",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".r": "R",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".dart": "Dart",
    ".lua": "Lua",
    ".pl": "Perl",
    ".sh": "Shell",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".less": "Less",
    ".vue": "Vue",
    ".svelte": "Svelte",
}


FRAMEWORK_PATTERNS = {
    "React": ["react", "react-dom", "react-router"],
    "Next.js": ["next", "next.js"],
    "Vue": ["vue", "vue-router", "vuex", "pinia"],
    "Svelte": ["svelte"],
    "Angular": ["@angular/core", "@angular/common"],
    "Express": ["express"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Spring": ["spring-boot", "springframework"],
    "ASP.NET": ["asp.net", "aspnetcore"],
    "Rails": ["rails"],
    "Laravel": ["laravel/framework"],
    "NestJS": ["@nestjs/core"],
    "Remix": ["@remix-run/react"],
    "Astro": ["astro"],
    "Nuxt": ["nuxt"],
}


SECRET_PATTERNS = [
    (r"api[_-]?key\s*[=:]\s*[\"'][a-zA-Z0-9_\-]{20,}[\"']", "API Key"),
    (r"secret[_-]?key\s*[=:]\s*[\"'][a-zA-Z0-9_\-]{20,}[\"']", "Secret Key"),
    (r"password\s*[=:]\s*[\"'][^\"']{8,}[\"']", "Password"),
    (r"token\s*[=:]\s*[\"'][a-zA-Z0-9_\-]{20,}[\"']", "Token"),
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private Key"),
    (r"[a-zA-Z0-9]{32,}", "Potential Secret"),
]


async def update_scan_progress(scan_id: UUID, progress: int, step: str):
    async with async_session_maker() as db:
        await db.execute(
            update(ScanSession)
            .where(ScanSession.id == scan_id)
            .values(progress=progress, current_step=step)
        )
        await db.commit()


async def save_scan_results(scan_id: UUID, results: Dict[str, Any]):
    async with async_session_maker() as db:
        await db.execute(
            update(ScanSession)
            .where(ScanSession.id == scan_id)
            .values(
                status=ScanStatus.COMPLETED,
                progress=100,
                current_step="Completed",
                languages=results.get("languages", []),
                frameworks=results.get("frameworks", []),
                dependencies=results.get("dependencies", []),
                issues=results.get("issues", []),
                secrets=results.get("secrets", []),
                total_files=results.get("total_files", 0),
                scanned_files=results.get("scanned_files", 0),
            )
        )
        
        for issue in results.get("issues", []):
            finding = ScanFinding(
                scan_session_id=scan_id,
                type=IssueType(issue["type"]),
                category=IssueCategory(issue["category"]),
                file=issue["file"],
                line=issue.get("line"),
                column=issue.get("column"),
                message=issue["message"],
                rule=issue.get("rule"),
                fixable=issue.get("fixable", False),
            )
            db.add(finding)
        
        for secret in results.get("secrets", []):
            secret_finding = SecretFinding(
                scan_session_id=scan_id,
                type=secret["type"],
                file=secret["file"],
                line=secret["line"],
                severity=RiskLevel(secret["severity"]),
                matched_content=secret["matched_content"],
            )
            db.add(secret_finding)
        
        await db.commit()


def detect_language(file_path: Path) -> str:
    return LANGUAGE_EXTENSIONS.get(file_path.suffix.lower(), "Unknown")


def detect_frameworks(project_path: Path) -> List[Dict[str, Any]]:
    frameworks = []
    package_json = project_path / "package.json"
    requirements_txt = project_path / "requirements.txt"
    pyproject_toml = project_path / "pyproject.toml"
    pom_xml = project_path / "pom.xml"
    build_gradle = project_path / "build.gradle"
    
    deps = set()
    
    if package_json.exists():
        import json
        try:
            data = json.loads(package_json.read_text())
            deps.update(data.get("dependencies", {}).keys())
            deps.update(data.get("devDependencies", {}).keys())
        except:
            pass
    
    if requirements_txt.exists():
        try:
            for line in requirements_txt.read_text().splitlines():
                if line.strip() and not line.startswith("#"):
                    deps.add(line.split("==")[0].split(">=")[0].split("<=")[0].strip())
        except:
            pass
    
    if pyproject_toml.exists():
        try:
            import toml
            data = toml.loads(pyproject_toml.read_text())
            deps.update(data.get("project", {}).get("dependencies", []))
            deps.update(data.get("tool", {}).get("poetry", {}).get("dependencies", {}).keys())
        except:
            pass
    
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for pattern in patterns:
            if any(pattern.lower() in dep.lower() for dep in deps):
                frameworks.append({"framework": framework, "confidence": 0.9})
                break
    
    return frameworks


def analyze_dependencies(project_path: Path) -> List[Dict[str, Any]]:
    dependencies = []
    package_json = project_path / "package.json"
    requirements_txt = project_path / "requirements.txt"
    
    if package_json.exists():
        import json
        try:
            data = json.loads(package_json.read_text())
            for name, version in data.get("dependencies", {}).items():
                dependencies.append({"name": name, "version": version, "status": "up-to-date"})
            for name, version in data.get("devDependencies", {}).items():
                dependencies.append({"name": name, "version": version, "status": "up-to-date"})
        except:
            pass
    
    if requirements_txt.exists():
        try:
            for line in requirements_txt.read_text().splitlines():
                if line.strip() and not line.startswith("#"):
                    parts = line.split("==")
                    if len(parts) == 2:
                        dependencies.append({"name": parts[0].strip(), "version": parts[1].strip(), "status": "up-to-date"})
                    else:
                        dependencies.append({"name": line.strip(), "version": "latest", "status": "unknown"})
        except:
            pass
    
    return dependencies


def scan_for_issues(project_path: Path) -> List[Dict[str, Any]]:
    issues = []
    
    for file_path in project_path.rglob("*"):
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
            if file_path.name in ["node_modules", "__pycache__", ".git", "venv", "env", "dist", "build"]:
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8")
                rel_path = file_path.relative_to(project_path)
                
                if file_path.suffix in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                    lines = content.splitlines()
                    for i, line in enumerate(lines, 1):
                        if "import " in line or "from " in line and "import" in line:
                            if "from '" in line or 'from "' in line:
                                import_path = line.split("from")[1].split("import")[0].strip().strip('"\'')
                                if import_path.startswith(".") or import_path.startswith("/"):
                                    target = (file_path.parent / import_path).resolve()
                                    if not target.exists():
                                        issues.append({
                                            "type": "error",
                                            "category": "import",
                                            "file": str(rel_path),
                                            "line": i,
                                            "message": f"Broken import: {import_path}",
                                            "rule": "broken-import",
                                            "fixable": False,
                                        })
                
                if "TODO" in content or "FIXME" in content:
                    for i, line in enumerate(content.splitlines(), 1):
                        if "TODO" in line or "FIXME" in line:
                            issues.append({
                                "type": "warning",
                                "category": "style",
                                "file": str(rel_path),
                                "line": i,
                                "message": f"TODO/FIXME comment found: {line.strip()}",
                                "rule": "todo-comment",
                                "fixable": False,
                            })
                            break
                
            except UnicodeDecodeError:
                pass
            except Exception:
                pass
    
    return issues


def scan_for_secrets(project_path: Path) -> List[Dict[str, Any]]:
    import re
    secrets = []
    
    for file_path in project_path.rglob("*"):
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
            if file_path.name in ["node_modules", "__pycache__", ".git", "venv", "env", "dist", "build"]:
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8")
                rel_path = file_path.relative_to(project_path)
                
                for i, line in enumerate(content.splitlines(), 1):
                    for pattern, secret_type in SECRET_PATTERNS:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        if matches:
                            secrets.append({
                                "type": secret_type,
                                "file": str(rel_path),
                                "line": i,
                                "severity": "high",
                                "matched_content": line.strip()[:100],
                            })
            except UnicodeDecodeError:
                pass
            except Exception:
                pass
    
    return secrets


def extract_features(project_path: Path) -> List[Dict[str, Any]]:
    features = []
    
    for file_path in project_path.rglob("*"):
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
            rel_path = file_path.relative_to(project_path)
            
            if file_path.suffix in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    
                    if "def " in content or "function " in content or "const " in content and "= (" in content:
                        feature_type = FeatureType.SERVICE
                        if "route" in str(rel_path).lower() or "api" in str(rel_path).lower() or "endpoint" in str(rel_path).lower():
                            feature_type = FeatureType.API
                        elif "component" in str(rel_path).lower() or "page" in str(rel_path).lower() or "view" in str(rel_path).lower():
                            feature_type = FeatureType.UI
                        elif "model" in str(rel_path).lower() or "schema" in str(rel_path).lower() or "database" in str(rel_path).lower():
                            feature_type = FeatureType.DATABASE
                        elif "auth" in str(rel_path).lower() or "login" in str(rel_path).lower() or "token" in str(rel_path).lower():
                            feature_type = FeatureType.AUTH
                        
                        features.append({
                            "name": rel_path.stem.replace("_", " ").replace("-", " ").title(),
                            "path": str(rel_path),
                            "type": feature_type.value,
                            "status": FeatureStatus.UNKNOWN.value,
                            "reliability_score": 0,
                            "dependencies": [],
                            "demo_path": False,
                        })
                except:
                    pass
    
    return features


@shared_task(bind=True, max_retries=3)
def scan_project_task(self, project_id: str):
    import asyncio
    
    async def _scan():
        project_uuid = UUID(project_id)
        
        async with async_session_maker() as db:
            result = await db.execute(select(Project).where(Project.id == project_uuid))
            project = result.scalar_one_or_none()
            if not project:
                logger.error("Project not found", project_id=project_id)
                return
            
            scan = ScanSession(
                project_id=project_uuid,
                status=ScanStatus.RUNNING,
                progress=0,
                current_step="Initializing scan",
            )
            db.add(scan)
            await db.commit()
            await db.refresh(scan)
            
            project.status = ScanStatus.SCANNING
            await db.commit()
        
        if not project.storage_path:
            await update_scan_progress(scan.id, 0, "No storage path")
            async with async_session_maker() as db:
                await db.execute(
                    update(ScanSession)
                    .where(ScanSession.id == scan.id)
                    .values(status=ScanStatus.FAILED, error="No storage path")
                )
                await db.commit()
            return
        
        project_path = Path(project.storage_path)
        
        await update_scan_progress(scan.id, 10, "Detecting languages")
        
        language_counts = {}
        total_files = 0
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
                if file_path.name not in ["node_modules", "__pycache__", ".git", "venv", "env", "dist", "build"]:
                    total_files += 1
                    lang = detect_language(file_path)
                    language_counts[lang] = language_counts.get(lang, 0) + 1
        
        languages = [
            {"language": lang, "files": count, "lines": 0, "percentage": round(count / total_files * 100, 1) if total_files > 0 else 0}
            for lang, count in language_counts.items()
        ]
        
        await update_scan_progress(scan.id, 30, "Detecting frameworks")
        frameworks = detect_frameworks(project_path)
        
        await update_scan_progress(scan.id, 50, "Analyzing dependencies")
        dependencies = analyze_dependencies(project_path)
        
        await update_scan_progress(scan.id, 70, "Scanning for issues")
        issues = scan_for_issues(project_path)
        
        await update_scan_progress(scan.id, 85, "Scanning for secrets")
        secrets = scan_for_secrets(project_path)
        
        await update_scan_progress(scan.id, 95, "Extracting features")
        features = extract_features(project_path)
        
        results = {
            "total_files": total_files,
            "scanned_files": total_files,
            "languages": languages,
            "frameworks": frameworks,
            "dependencies": dependencies,
            "issues": issues,
            "secrets": secrets,
        }
        
        await save_scan_results(scan.id, results)
        
        async with async_session_maker() as db:
            for feature_data in features:
                feature = Feature(
                    project_id=project_uuid,
                    name=feature_data["name"],
                    path=feature_data["path"],
                    type=FeatureType(feature_data["type"]),
                    status=FeatureStatus(feature_data["status"]),
                    reliability_score=feature_data["reliability_score"],
                    dependencies=feature_data["dependencies"],
                    demo_path=feature_data["demo_path"],
                )
                db.add(feature)
            
            project.status = "analyzed"
            project.critical_issues = len([i for i in issues if i["type"] == "error"])
            await db.commit()
        
        logger.info("Scan completed", project_id=project_id, scan_id=str(scan.id))
    
    try:
        asyncio.run(_scan())
    except Exception as e:
        logger.error("Scan failed", project_id=project_id, error=str(e))
        asyncio.run(update_scan_progress(UUID(project_id), 0, f"Failed: {str(e)}"))
        raise