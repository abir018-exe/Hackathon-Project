export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: "owner" | "admin" | "developer" | "viewer";
  createdAt: string;
  updatedAt: string;
}

export interface Team {
  id: string;
  name: string;
  slug: string;
  description?: string;
  avatar?: string;
  ownerId: string;
  members: TeamMember[];
  createdAt: string;
  updatedAt: string;
}

export interface TeamMember {
  id: string;
  userId: string;
  teamId: string;
  role: "owner" | "admin" | "developer" | "viewer";
  user: User;
  joinedAt: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  teamId: string;
  repositoryUrl?: string;
  branch: string;
  framework?: string;
  language?: string;
  status: "pending" | "scanning" | "analyzed" | "stabilizing" | "ready" | "error";
  demoSurvivalScore?: number;
  criticalIssues: number;
  featureReliability?: number;
  demoReadiness?: number;
  lastScanAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ScanSession {
  id: string;
  projectId: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  currentStep: string;
  totalFiles: number;
  scannedFiles: number;
  languages: LanguageStats[];
  frameworks: FrameworkStats[];
  dependencies: DependencyStats[];
  issues: ScanIssue[];
  secrets: SecretFinding[];
  startedAt: string;
  completedAt?: string;
  error?: string;
}

export interface LanguageStats {
  language: string;
  files: number;
  lines: number;
  percentage: number;
}

export interface FrameworkStats {
  framework: string;
  version?: string;
  confidence: number;
}

export interface DependencyStats {
  name: string;
  version: string;
  latestVersion?: string;
  status: "up-to-date" | "outdated" | "vulnerable" | "missing";
  severity?: "low" | "medium" | "high" | "critical";
  license?: string;
}

export interface ScanIssue {
  id: string;
  type: "error" | "warning" | "info";
  category: "import" | "dependency" | "config" | "security" | "performance" | "style";
  file: string;
  line?: number;
  column?: number;
  message: string;
  rule?: string;
  fixable: boolean;
}

export interface SecretFinding {
  id: string;
  type: string;
  file: string;
  line: number;
  severity: "low" | "medium" | "high" | "critical";
  matchedContent: string;
}

export interface Feature {
  id: string;
  projectId: string;
  name: string;
  description?: string;
  path: string;
  type: "api" | "ui" | "service" | "database" | "auth" | "integration";
  status: "unknown" | "stable" | "unstable" | "critical" | "mocked";
  reliabilityScore: number;
  dependencies: string[];
  testCoverage?: number;
  lastTestedAt?: string;
  demoPath: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface FeatureDependency {
  id: string;
  projectId: string;
  sourceFeatureId: string;
  targetFeatureId: string;
  type: "requires" | "optional" | "conflicts";
  strength: "strong" | "weak";
}

export interface RiskAssessment {
  id: string;
  projectId: string;
  overallScore: number;
  riskLevel: "critical" | "high" | "medium" | "low";
  riskDistribution: Record<string, number>;
  featureScores: FeatureRiskScore[];
  failurePredictions: FailurePrediction[];
  happyPaths: HappyPath[];
  dependencyRisks: DependencyRisk[];
  aiRecommendations: AIRecommendation[];
  createdAt: string;
  updatedAt: string;
}

export interface FeatureRiskScore {
  featureId: string;
  featureName: string;
  score: number;
  riskLevel: "critical" | "high" | "medium" | "low";
  factors: RiskFactor[];
  demoValue: number;
}

export interface RiskFactor {
  type: string;
  impact: number;
  description: string;
  evidence: string;
}

export interface FailurePrediction {
  id: string;
  featureId: string;
  featureName: string;
  probability: number;
  impact: "critical" | "high" | "medium" | "low";
  description: string;
  mitigations: string[];
  isEstimate: boolean;
}

export interface HappyPath {
  id: string;
  name: string;
  description: string;
  features: string[];
  reliability: number;
  steps: HappyPathStep[];
  estimatedDuration: number;
}

export interface HappyPathStep {
  featureId: string;
  featureName: string;
  action: string;
  expectedResult: string;
}

export interface DependencyRisk {
  dependency: string;
  riskLevel: "critical" | "high" | "medium" | "low";
  reason: string;
  affectedFeatures: string[];
}

export interface AIRecommendation {
  id: string;
  type: "stabilization" | "mock" | "fallback" | "config" | "test" | "refactor";
  priority: "critical" | "high" | "medium" | "low";
  title: string;
  description: string;
  affectedFiles: string[];
  estimatedEffort: "low" | "medium" | "high";
  expectedImpact: string;
  confidence: number;
  isEstimate: boolean;
}

export interface StabilizationTask {
  id: string;
  projectId: string;
  title: string;
  description: string;
  type: "patch" | "mock" | "fallback" | "config" | "test" | "refactor";
  status: "pending" | "approved" | "rejected" | "applied" | "rolled_back" | "testing";
  priority: "critical" | "high" | "medium" | "low";
  files: StabilizationFile[];
  aiRecommendationId?: string;
  createdBy: string;
  approvedBy?: string;
  appliedAt?: string;
  rolledBackAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface StabilizationFile {
  path: string;
  originalContent: string;
  proposedContent: string;
  diff: string;
  reason: string;
  expectedImpact: string;
  riskLevel: "critical" | "high" | "medium" | "low";
  approved: boolean;
}

export interface Patch {
  id: string;
  taskId: string;
  filePath: string;
  originalContent: string;
  modifiedContent: string;
  diff: string;
  status: "pending" | "approved" | "rejected" | "applied" | "rolled_back";
  approvedBy?: string;
  appliedAt?: string;
  rolledBackAt?: string;
  createdAt: string;
}

export interface TestExecution {
  id: string;
  projectId: string;
  scanSessionId?: string;
  stabilizationTaskId?: string;
  type: "smoke" | "happy_path" | "api" | "ui" | "regression" | "environment" | "demo_readiness";
  status: "pending" | "running" | "passed" | "failed" | "skipped" | "unverified";
  tests: TestCase[];
  passedCount: number;
  failedCount: number;
  skippedCount: number;
  totalDuration: number;
  environment: TestEnvironment;
  startedAt: string;
  completedAt?: string;
  error?: string;
}

export interface TestCase {
  id: string;
  name: string;
  category: string;
  status: "passed" | "failed" | "running" | "skipped" | "unverified";
  duration: number;
  error?: string;
  details?: Record<string, unknown>;
  lastExecutedAt: string;
}

export interface TestEnvironment {
  id: string;
  name: string;
  type: "local" | "docker" | "ci" | "demo";
  config: Record<string, unknown>;
  status: "ready" | "building" | "running" | "stopped" | "error";
}

export interface DemoConfiguration {
  id: string;
  projectId: string;
  name: string;
  enabled: boolean;
  mockData: MockDataConfig[];
  apiFallbacks: APIFallbackConfig[];
  featureFlags: FeatureFlagConfig[];
  environmentVariables: Record<string, string>;
  createdAt: string;
  updatedAt: string;
}

export interface MockDataConfig {
  id: string;
  featureId: string;
  data: Record<string, unknown>;
  source: "ai_generated" | "user_provided" | "sample";
  enabled: boolean;
}

export interface APIFallbackConfig {
  id: string;
  endpoint: string;
  method: string;
  fallbackResponse: Record<string, unknown>;
  conditions: string[];
  enabled: boolean;
}

export interface FeatureFlagConfig {
  id: string;
  featureId: string;
  enabled: boolean;
  rolloutPercentage: number;
  conditions: string[];
}

export interface DemoScript {
  id: string;
  projectId: string;
  title: string;
  durationMinutes: number;
  audience: "technical" | "non-technical" | "mixed" | "judges";
  sections: DemoScriptSection[];
  verifiedFeaturesOnly: boolean;
  generatedAt: string;
  updatedAt: string;
}

export interface DemoScriptSection {
  id: string;
  type: "intro" | "problem" | "overview" | "demo" | "architecture" | "results" | "conclusion" | "qa";
  title: string;
  content: string;
  durationMinutes: number;
  features: string[];
  talkingPoints: string[];
  backupContent?: string;
}

export interface ActivityLog {
  id: string;
  projectId: string;
  userId: string;
  action: string;
  entityType: string;
  entityId: string;
  metadata: Record<string, unknown>;
  createdAt: string;
}

export interface Notification {
  id: string;
  userId: string;
  type: "info" | "warning" | "error" | "success";
  title: string;
  message: string;
  read: boolean;
  actionUrl?: string;
  createdAt: string;
}

export interface GitCommit {
  id: string;
  projectId: string;
  sha: string;
  message: string;
  author: string;
  authorEmail: string;
  timestamp: string;
  filesChanged: GitFileChange[];
  riskLevel: "critical" | "high" | "medium" | "low";
  riskReason?: string;
  affectsDemoPath: boolean;
}

export interface GitFileChange {
  path: string;
  status: "added" | "modified" | "deleted" | "renamed";
  additions: number;
  deletions: number;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}