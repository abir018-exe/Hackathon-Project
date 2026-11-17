import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, DateTime, ForeignKey, Enum, Boolean,
    Index, JSON, BigInteger, Float, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from app.db.session import Base


class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    ANALYZED = "analyzed"
    STABILIZING = "stabilizing"
    READY = "ready"
    ERROR = "error"


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueType(str, enum.Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(str, enum.Enum):
    IMPORT = "import"
    DEPENDENCY = "dependency"
    CONFIG = "config"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"


class RiskLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FeatureType(str, enum.Enum):
    API = "api"
    UI = "ui"
    SERVICE = "service"
    DATABASE = "database"
    AUTH = "auth"
    INTEGRATION = "integration"


class FeatureStatus(str, enum.Enum):
    UNKNOWN = "unknown"
    STABLE = "stable"
    UNSTABLE = "unstable"
    CRITICAL = "critical"
    MOCKED = "mocked"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    TESTING = "testing"


class TaskType(str, enum.Enum):
    PATCH = "patch"
    MOCK = "mock"
    FALLBACK = "fallback"
    CONFIG = "config"
    TEST = "test"
    REFACTOR = "refactor"


class TestStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNVERIFIED = "unverified"


class TestType(str, enum.Enum):
    SMOKE = "smoke"
    HAPPY_PATH = "happy_path"
    API = "api"
    UI = "ui"
    REGRESSION = "regression"
    ENVIRONMENT = "environment"
    DEMO_READINESS = "demo_readiness"


class DemoScriptType(str, enum.Enum):
    INTRO = "intro"
    PROBLEM = "problem"
    OVERVIEW = "overview"
    DEMO = "demo"
    ARCHITECTURE = "architecture"
    RESULTS = "results"
    CONCLUSION = "conclusion"
    QA = "qa"


class NotificationType(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class GitFileStatus(str, enum.Enum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.DEVELOPER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team_memberships: Mapped[List["TeamMember"]] = relationship(back_populates="user")
    owned_teams: Mapped[List["Team"]] = relationship(back_populates="owner")
    activity_logs: Mapped[List["ActivityLog"]] = relationship(back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    
    __table_args__ = (
        Index("ix_users_email", "email"),
    )


class Team(Base):
    __tablename__ = "teams"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner: Mapped["User"] = relationship(back_populates="owned_teams")
    members: Mapped[List["TeamMember"]] = relationship(back_populates="team")
    projects: Mapped[List["Project"]] = relationship(back_populates="team")
    
    __table_args__ = (
        Index("ix_teams_slug", "slug"),
    )


class TeamMember(Base):
    __tablename__ = "team_members"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.DEVELOPER, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="team_memberships")
    team: Mapped["Team"] = relationship(back_populates="members")
    
    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uq_user_team"),
        Index("ix_team_members_user_id", "user_id"),
        Index("ix_team_members_team_id", "team_id"),
    )


class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    repository_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    framework: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.PENDING, nullable=False)
    demo_survival_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    critical_issues: Mapped[int] = mapped_column(Integer, default=0)
    feature_reliability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    demo_readiness: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_scan_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team: Mapped["Team"] = relationship(back_populates="projects")
    scan_sessions: Mapped[List["ScanSession"]] = relationship(back_populates="project")
    features: Mapped[List["Feature"]] = relationship(back_populates="project")
    risk_assessments: Mapped[List["RiskAssessment"]] = relationship(back_populates="project")
    stabilization_tasks: Mapped[List["StabilizationTask"]] = relationship(back_populates="project")
    test_executions: Mapped[List["TestExecution"]] = relationship(back_populates="project")
    demo_configs: Mapped[List["DemoConfiguration"]] = relationship(back_populates="project")
    demo_scripts: Mapped[List["DemoScript"]] = relationship(back_populates="project")
    activity_logs: Mapped[List["ActivityLog"]] = relationship(back_populates="project")
    git_commits: Mapped[List["GitCommit"]] = relationship(back_populates="project")
    
    __table_args__ = (
        Index("ix_projects_team_id", "team_id"),
        Index("ix_projects_status", "status"),
    )


class ScanSession(Base):
    __tablename__ = "scan_sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    status: Mapped[ScanStatus] = mapped_column(Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str] = mapped_column(String(200), default="")
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    scanned_files: Mapped[int] = mapped_column(Integer, default=0)
    languages: Mapped[List[dict]] = mapped_column(JSON, default=list)
    frameworks: Mapped[List[dict]] = mapped_column(JSON, default=list)
    dependencies: Mapped[List[dict]] = mapped_column(JSON, default=list)
    issues: Mapped[List[dict]] = mapped_column(JSON, default=list)
    secrets: Mapped[List[dict]] = mapped_column(JSON, default=list)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="scan_sessions")
    findings: Mapped[List["ScanFinding"]] = relationship(back_populates="scan_session")
    
    __table_args__ = (
        Index("ix_scan_sessions_project_id", "project_id"),
        Index("ix_scan_sessions_status", "status"),
    )


class ScanFinding(Base):
    __tablename__ = "scan_findings"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scan_sessions.id"), nullable=False)
    type: Mapped[IssueType] = mapped_column(Enum(IssueType), nullable=False)
    category: Mapped[IssueCategory] = mapped_column(Enum(IssueCategory), nullable=False)
    file: Mapped[str] = mapped_column(String(500), nullable=False)
    line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    column: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    rule: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    fixable: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    scan_session: Mapped["ScanSession"] = relationship(back_populates="findings")
    
    __table_args__ = (
        Index("ix_scan_findings_scan_session_id", "scan_session_id"),
        Index("ix_scan_findings_type_category", "type", "category"),
    )


class SecretFinding(Base):
    __tablename__ = "secret_findings"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scan_sessions.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    file: Mapped[str] = mapped_column(String(500), nullable=False)
    line: Mapped[int] = mapped_column(Integer, nullable=False)
    severity: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    matched_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_secret_findings_scan_session_id", "scan_session_id"),
        Index("ix_secret_findings_severity", "severity"),
    )


class Feature(Base):
    __tablename__ = "features"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[FeatureType] = mapped_column(Enum(FeatureType), nullable=False)
    status: Mapped[FeatureStatus] = mapped_column(Enum(FeatureStatus), default=FeatureStatus.UNKNOWN, nullable=False)
    reliability_score: Mapped[int] = mapped_column(Integer, default=0)
    dependencies: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    test_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_tested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    demo_path: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="features")
    source_dependencies: Mapped[List["FeatureDependency"]] = relationship(back_populates="source_feature", foreign_keys="FeatureDependency.source_feature_id")
    target_dependencies: Mapped[List["FeatureDependency"]] = relationship(back_populates="target_feature", foreign_keys="FeatureDependency.target_feature_id")
    
    __table_args__ = (
        Index("ix_features_project_id", "project_id"),
        Index("ix_features_type", "type"),
        Index("ix_features_status", "status"),
    )


class FeatureDependency(Base):
    __tablename__ = "feature_dependencies"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    source_feature_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("features.id"), nullable=False)
    target_feature_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("features.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="requires")
    strength: Mapped[str] = mapped_column(String(50), default="strong")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    source_feature: Mapped["Feature"] = relationship(back_populates="source_dependencies", foreign_keys=[source_feature_id])
    target_feature: Mapped["Feature"] = relationship(back_populates="target_dependencies", foreign_keys=[target_feature_id])
    
    __table_args__ = (
        UniqueConstraint("source_feature_id", "target_feature_id", name="uq_feature_dependency"),
        Index("ix_feature_dependencies_project_id", "project_id"),
    )


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), default=RiskLevel.LOW, nullable=False)
    risk_distribution: Mapped[dict] = mapped_column(JSON, default=dict)
    feature_scores: Mapped[List[dict]] = mapped_column(JSON, default=list)
    failure_predictions: Mapped[List[dict]] = mapped_column(JSON, default=list)
    happy_paths: Mapped[List[dict]] = mapped_column(JSON, default=list)
    dependency_risks: Mapped[List[dict]] = mapped_column(JSON, default=list)
    ai_recommendations: Mapped[List[dict]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="risk_assessments")
    
    __table_args__ = (
        Index("ix_risk_assessments_project_id", "project_id"),
    )


class StabilizationTask(Base):
    __tablename__ = "stabilization_tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[TaskType] = mapped_column(Enum(TaskType), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), default=RiskLevel.MEDIUM, nullable=False)
    files: Mapped[List[dict]] = mapped_column(JSON, default=list)
    ai_recommendation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rolled_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="stabilization_tasks")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    approver: Mapped[Optional["User"]] = relationship(foreign_keys=[approved_by])
    patches: Mapped[List["Patch"]] = relationship(back_populates="task")
    
    __table_args__ = (
        Index("ix_stabilization_tasks_project_id", "project_id"),
        Index("ix_stabilization_tasks_status", "status"),
    )


class Patch(Base):
    __tablename__ = "patches"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stabilization_tasks.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_content: Mapped[str] = mapped_column(Text, nullable=False)
    modified_content: Mapped[str] = mapped_column(Text, nullable=False)
    diff: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rolled_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    task: Mapped["StabilizationTask"] = relationship(back_populates="patches")
    approver: Mapped[Optional["User"]] = relationship()
    
    __table_args__ = (
        Index("ix_patches_task_id", "task_id"),
        Index("ix_patches_status", "status"),
    )


class TestExecution(Base):
    __tablename__ = "test_executions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    scan_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("scan_sessions.id"), nullable=True)
    stabilization_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("stabilization_tasks.id"), nullable=True)
    type: Mapped[TestType] = mapped_column(Enum(TestType), nullable=False)
    status: Mapped[TestStatus] = mapped_column(Enum(TestStatus), default=TestStatus.PENDING, nullable=False)
    tests: Mapped[List[dict]] = mapped_column(JSON, default=list)
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    total_duration: Mapped[int] = mapped_column(Integer, default=0)
    environment: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="test_executions")
    scan_session: Mapped[Optional["ScanSession"]] = relationship()
    stabilization_task: Mapped[Optional["StabilizationTask"]] = relationship()
    
    __table_args__ = (
        Index("ix_test_executions_project_id", "project_id"),
        Index("ix_test_executions_status", "status"),
    )


class DemoConfiguration(Base):
    __tablename__ = "demo_configurations"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), default="Default Demo Config")
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mock_data: Mapped[List[dict]] = mapped_column(JSON, default=list)
    api_fallbacks: Mapped[List[dict]] = mapped_column(JSON, default=list)
    feature_flags: Mapped[List[dict]] = mapped_column(JSON, default=list)
    environment_variables: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="demo_configs")
    
    __table_args__ = (
        Index("ix_demo_configurations_project_id", "project_id"),
    )


class DemoScript(Base):
    __tablename__ = "demo_scripts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=10)
    audience: Mapped[str] = mapped_column(String(50), default="judges")
    sections: Mapped[List[dict]] = mapped_column(JSON, default=list)
    verified_features_only: Mapped[bool] = mapped_column(Boolean, default=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="demo_scripts")
    
    __table_args__ = (
        Index("ix_demo_scripts_project_id", "project_id"),
    )


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="activity_logs")
    user: Mapped["User"] = relationship(back_populates="activity_logs")
    
    __table_args__ = (
        Index("ix_activity_logs_project_id", "project_id"),
        Index("ix_activity_logs_user_id", "user_id"),
        Index("ix_activity_logs_created_at", "created_at"),
    )


class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="notifications")
    
    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_read", "read"),
        Index("ix_notifications_created_at", "created_at"),
    )


class GitCommit(Base):
    __tablename__ = "git_commits"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    sha: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(200), nullable=False)
    author_email: Mapped[str] = mapped_column(String(200), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    files_changed: Mapped[List[dict]] = mapped_column(JSON, default=list)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), default=RiskLevel.LOW, nullable=False)
    risk_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    affects_demo_path: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="git_commits")
    
    __table_args__ = (
        Index("ix_git_commits_project_id", "project_id"),
        Index("ix_git_commits_sha", "sha"),
    )