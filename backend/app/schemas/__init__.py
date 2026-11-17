from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from uuid import UUID
import enum


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


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    avatar: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar: Optional[str] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: UUID
    exp: int
    type: str


# Team Schemas
class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    avatar: Optional[str] = None


class TeamMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    team_id: UUID
    role: UserRole
    joined_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True


class TeamResponse(TeamBase):
    id: UUID
    avatar: Optional[str]
    owner_id: UUID
    owner: UserResponse
    members: List[TeamMemberResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    repository_url: Optional[HttpUrl] = None
    branch: str = "main"


class ProjectCreate(ProjectBase):
    team_id: UUID


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    repository_url: Optional[HttpUrl] = None
    branch: Optional[str] = None
    framework: Optional[str] = None
    language: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: UUID
    team_id: UUID
    framework: Optional[str]
    language: Optional[str]
    status: ProjectStatus
    demo_survival_score: Optional[int]
    critical_issues: int
    feature_reliability: Optional[float]
    demo_readiness: Optional[int]
    last_scan_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Scan Session Schemas
class LanguageStats(BaseModel):
    language: str
    files: int
    lines: int
    percentage: float


class FrameworkStats(BaseModel):
    framework: str
    version: Optional[str] = None
    confidence: float


class DependencyStats(BaseModel):
    name: str
    version: str
    latest_version: Optional[str] = None
    status: str
    severity: Optional[str] = None
    license: Optional[str] = None


class ScanIssue(BaseModel):
    id: str
    type: IssueType
    category: IssueCategory
    file: str
    line: Optional[int] = None
    column: Optional[int] = None
    message: str
    rule: Optional[str] = None
    fixable: bool


class SecretFinding(BaseModel):
    id: str
    type: str
    file: str
    line: int
    severity: RiskLevel
    matched_content: str


class ScanSessionBase(BaseModel):
    project_id: UUID


class ScanSessionCreate(ScanSessionBase):
    pass


class ScanSessionUpdate(BaseModel):
    status: Optional[ScanStatus] = None
    progress: Optional[int] = None
    current_step: Optional[str] = None
    total_files: Optional[int] = None
    scanned_files: Optional[int] = None
    languages: Optional[List[LanguageStats]] = None
    frameworks: Optional[List[FrameworkStats]] = None
    dependencies: Optional[List[DependencyStats]] = None
    issues: Optional[List[ScanIssue]] = None
    secrets: Optional[List[SecretFinding]] = None
    error: Optional[str] = None


class ScanSessionResponse(ScanSessionBase):
    id: UUID
    status: ScanStatus
    progress: int
    current_step: str
    total_files: int
    scanned_files: int
    languages: List[LanguageStats]
    frameworks: List[FrameworkStats]
    dependencies: List[DependencyStats]
    issues: List[ScanIssue]
    secrets: List[SecretFinding]
    error: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Feature Schemas
class FeatureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    path: str
    type: FeatureType


class FeatureCreate(FeatureBase):
    project_id: UUID


class FeatureUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[FeatureStatus] = None
    reliability_score: Optional[int] = None
    dependencies: Optional[List[str]] = None
    test_coverage: Optional[float] = None
    demo_path: Optional[bool] = None


class FeatureResponse(FeatureBase):
    id: UUID
    project_id: UUID
    status: FeatureStatus
    reliability_score: int
    dependencies: List[str]
    test_coverage: Optional[float]
    last_tested_at: Optional[datetime]
    demo_path: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Risk Assessment Schemas
class RiskFactor(BaseModel):
    type: str
    impact: float
    description: str
    evidence: str


class FeatureRiskScore(BaseModel):
    feature_id: str
    feature_name: str
    score: int
    risk_level: RiskLevel
    factors: List[RiskFactor]
    demo_value: float


class FailurePrediction(BaseModel):
    id: str
    feature_id: str
    feature_name: str
    probability: float
    impact: RiskLevel
    description: str
    mitigations: List[str]
    is_estimate: bool


class HappyPathStep(BaseModel):
    feature_id: str
    feature_name: str
    action: str
    expected_result: str


class HappyPath(BaseModel):
    id: str
    name: str
    description: str
    features: List[str]
    reliability: float
    steps: List[HappyPathStep]
    estimated_duration: int


class DependencyRisk(BaseModel):
    dependency: str
    risk_level: RiskLevel
    reason: str
    affected_features: List[str]


class AIRecommendation(BaseModel):
    id: str
    type: str
    priority: RiskLevel
    title: str
    description: str
    affected_files: List[str]
    estimated_effort: str
    expected_impact: str
    confidence: float
    is_estimate: bool


class RiskAssessmentResponse(BaseModel):
    id: UUID
    project_id: UUID
    overall_score: int
    risk_level: RiskLevel
    risk_distribution: Dict[str, int]
    feature_scores: List[FeatureRiskScore]
    failure_predictions: List[FailurePrediction]
    happy_paths: List[HappyPath]
    dependency_risks: List[DependencyRisk]
    ai_recommendations: List[AIRecommendation]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stabilization Schemas
class StabilizationFile(BaseModel):
    path: str
    original_content: str
    proposed_content: str
    diff: str
    reason: str
    expected_impact: str
    risk_level: RiskLevel
    approved: bool = False


class StabilizationTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str
    type: TaskType
    priority: RiskLevel


class StabilizationTaskCreate(StabilizationTaskBase):
    project_id: UUID
    files: List[StabilizationFile]
    ai_recommendation_id: Optional[str] = None


class StabilizationTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[RiskLevel] = None
    files: Optional[List[StabilizationFile]] = None


class StabilizationTaskResponse(StabilizationTaskBase):
    id: UUID
    project_id: UUID
    status: TaskStatus
    files: List[StabilizationFile]
    ai_recommendation_id: Optional[str]
    created_by: UUID
    approved_by: Optional[UUID]
    applied_at: Optional[datetime]
    rolled_back_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatchResponse(BaseModel):
    id: UUID
    task_id: UUID
    file_path: str
    original_content: str
    modified_content: str
    diff: str
    status: str
    approved_by: Optional[UUID]
    applied_at: Optional[datetime]
    rolled_back_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Testing Schemas
class TestCase(BaseModel):
    id: str
    name: str
    category: str
    status: TestStatus
    duration: int
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    last_executed_at: datetime


class TestExecutionBase(BaseModel):
    project_id: UUID
    type: TestType


class TestExecutionCreate(TestExecutionBase):
    scan_session_id: Optional[UUID] = None
    stabilization_task_id: Optional[UUID] = None


class TestExecutionResponse(TestExecutionBase):
    id: UUID
    scan_session_id: Optional[UUID]
    stabilization_task_id: Optional[UUID]
    status: TestStatus
    tests: List[TestCase]
    passed_count: int
    failed_count: int
    skipped_count: int
    total_duration: int
    environment: Dict[str, Any]
    error: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Demo Configuration Schemas
class MockDataConfig(BaseModel):
    id: str
    feature_id: str
    data: Dict[str, Any]
    source: str
    enabled: bool


class APIFallbackConfig(BaseModel):
    id: str
    endpoint: str
    method: str
    fallback_response: Dict[str, Any]
    conditions: List[str]
    enabled: bool


class FeatureFlagConfig(BaseModel):
    id: str
    feature_id: str
    enabled: bool
    rollout_percentage: float
    conditions: List[str]


class DemoConfigurationBase(BaseModel):
    name: str = "Default Demo Config"
    enabled: bool = False


class DemoConfigurationCreate(DemoConfigurationBase):
    project_id: UUID
    mock_data: List[MockDataConfig] = []
    api_fallbacks: List[APIFallbackConfig] = []
    feature_flags: List[FeatureFlagConfig] = []
    environment_variables: Dict[str, str] = {}


class DemoConfigurationUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    mock_data: Optional[List[MockDataConfig]] = None
    api_fallbacks: Optional[List[APIFallbackConfig]] = None
    feature_flags: Optional[List[FeatureFlagConfig]] = None
    environment_variables: Optional[Dict[str, str]] = None


class DemoConfigurationResponse(DemoConfigurationBase):
    id: UUID
    project_id: UUID
    mock_data: List[MockDataConfig]
    api_fallbacks: List[APIFallbackConfig]
    feature_flags: List[FeatureFlagConfig]
    environment_variables: Dict[str, str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Demo Script Schemas
class DemoScriptSection(BaseModel):
    id: str
    type: str
    title: str
    content: str
    duration_minutes: int
    features: List[str]
    talking_points: List[str]
    backup_content: Optional[str] = None


class DemoScriptBase(BaseModel):
    title: str
    duration_minutes: int = 10
    audience: str = "judges"
    verified_features_only: bool = True


class DemoScriptCreate(DemoScriptBase):
    project_id: UUID
    sections: List[DemoScriptSection] = []


class DemoScriptUpdate(BaseModel):
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    audience: Optional[str] = None
    sections: Optional[List[DemoScriptSection]] = None
    verified_features_only: Optional[bool] = None


class DemoScriptResponse(DemoScriptBase):
    id: UUID
    project_id: UUID
    sections: List[DemoScriptSection]
    generated_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Activity & Notification Schemas
class ActivityLogResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    read: bool
    action_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Git Commit Schemas
class GitFileChange(BaseModel):
    path: str
    status: GitFileStatus
    additions: int
    deletions: int


class GitCommitResponse(BaseModel):
    id: UUID
    project_id: UUID
    sha: str
    message: str
    author: str
    author_email: str
    timestamp: datetime
    files_changed: List[GitFileChange]
    risk_level: RiskLevel
    risk_reason: Optional[str]
    affects_demo_path: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Pagination
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# Generic Response
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None