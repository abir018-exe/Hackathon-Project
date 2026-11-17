"use client";

import * as React from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { formatRelativeTime, truncate } from "@/lib/utils";
import { useAppStore } from "@/store";
import { useProjects, useProject, useRiskAssessment, useScanProject, useScanSession } from "@/hooks/useApi";
import {
  Zap,
  AlertTriangle,
  Target,
  CheckCircle,
  Clock,
  Github,
  RefreshCw,
  TrendingUp,
  Activity,
  FileCode,
  Brain,
  Wrench,
  Monitor,
  Shield,
  TestTube2,
  FileText,
  Users,
  BarChart3,
  ArrowRight,
  ChevronRight,
  ExternalLink,
  Plus,
} from "lucide-react";

const riskColors = {
  critical: "bg-red-600",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-green-600",
};

const riskLabels = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

const statusColors = {
  pending: "bg-gray-500",
  scanning: "bg-blue-500",
  analyzed: "bg-green-500",
  stabilizing: "bg-purple-500",
  ready: "bg-green-500",
  error: "bg-red-500",
};

const statusLabels = {
  pending: "Pending",
  scanning: "Scanning",
  analyzed: "Analyzed",
  stabilizing: "Stabilizing",
  ready: "Ready",
  error: "Error",
};

export default function DashboardPage() {
  const { currentProject, currentTeam, setCurrentProject, projects } = useAppStore();
  const { data: projectsData, isLoading: projectsLoading } = useProjects(currentTeam?.id);
  const { data: projectData, isLoading: projectLoading } = useProject(currentProject?.id || "");
  const { data: riskData, isLoading: riskLoading } = useRiskAssessment(currentProject?.id || "");
  const scanProject = useScanProject();
  const { data: scanSession, isLoading: scanLoading } = useScanSession(currentProject?.id || "");

  const project = projectData || currentProject;
  const riskAssessment = riskData;
  const demoSurvivalScore = riskAssessment?.overallScore || 0;
  const riskLevel = riskAssessment?.riskLevel || "low";

  const recentActivity = [
    { id: "1", action: "Scan completed", entity: "project", time: "2 min ago", type: "scan" },
    { id: "2", action: "Patch approved", entity: "auth-service.ts", time: "15 min ago", type: "patch" },
    { id: "3", action: "Test execution passed", entity: "happy-path-checkout", time: "1 hour ago", type: "test" },
    { id: "4", action: "Demo mode activated", entity: "project", time: "3 hours ago", type: "demo" },
    { id: "5", action: "Risk assessment updated", entity: "project", time: "5 hours ago", type: "risk" },
  ];

  const criticalIssues = riskAssessment?.featureScores
    ?.filter((f) => f.riskLevel === "critical" || f.riskLevel === "high")
    .slice(0, 5) || [];

  const recommendedActions = [
    { id: "1", title: "Fix broken imports in api/client.ts", priority: "critical", href: "/stabilization" },
    { id: "2", title: "Add mock data for payment service", priority: "high", href: "/stabilization" },
    { id: "3", title: "Configure API fallback for external auth", priority: "high", href: "/demo-mode" },
    { id: "4", title: "Run happy path tests", priority: "medium", href: "/testing" },
    { id: "5", title: "Enable Demo Freeze Mode", priority: "medium", href: "/risk-monitor" },
  ];

  if (projectsLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 w-1/4 bg-lms-background-card rounded" style={{ backgroundColor: "#141925" }} />
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-32 bg-lms-background-card rounded-lg" style={{ backgroundColor: "#141925" }} />
              ))}
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!project) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto text-center py-20">
          <Zap className="mx-auto h-16 w-16 text-muted-foreground mb-6" style={{ color: "#8B7CFF" }} />
          <h1 className="text-3xl font-bold text-white mb-4">No Project Selected</h1>
          <p className="text-muted-foreground mb-8 max-w-md mx-auto">
            Select a project from the sidebar or create a new one to start stabilizing your codebase.
          </p>
          <Button size="lg" onClick={() => {}} style={{ backgroundColor: "#8B7CFF", color: "#090B10" }}>
            <Plus className="h-4 w-4 mr-2" />
            Create New Project
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl lg:text-3xl font-bold text-white">{project.name}</h1>
              <Badge variant="outline" className={cn("gap-1", statusColors[project.status])}>
                <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: statusColors[project.status] }} />
                {statusLabels[project.status]}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              {project.repositoryUrl && (
                <a href={project.repositoryUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 hover:text-foreground transition-colors">
                  <Github className="h-4 w-4" />
                  {project.branch}
                </a>
              )}
              <span>Last scanned {project.lastScanAt ? formatRelativeTime(project.lastScanAt) : "never"}</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => scanProject.mutate(project.id)} disabled={scanProject.isPending}>
              <RefreshCw className={cn("h-4 w-4 mr-2", scanProject.isPending && "animate-spin")} />
              Scan Project
            </Button>
            <Button style={{ backgroundColor: "#8B7CFF", color: "#090B10" }}>
              <ArrowRight className="h-4 w-4 mr-2" />
              View Details
            </Button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Demo Survival Score</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" style={{ color: "#35C98A" }} />
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-2">
                <span className="text-4xl font-bold text-white">{demoSurvivalScore}</span>
                <span className="text-muted-foreground">/ 100</span>
              </div>
              <Progress value={demoSurvivalScore} className="mt-4 h-2" />
              <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                <span>{riskLabels[riskLevel]} Risk</span>
                <Badge variant="outline" className={riskColors[riskLevel]}>{riskLabels[riskLevel]}</Badge>
              </div>
            </CardContent>
          </Card>

          <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Critical Issues</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" style={{ color: "#F16C78" }} />
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-white">{project.criticalIssues || 0}</div>
              <p className="text-sm text-muted-foreground mt-1">
                {criticalIssues.length} high-priority items need attention
              </p>
            </CardContent>
          </Card>

          <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Feature Reliability</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" style={{ color: "#36C8F0" }} />
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-white">{riskAssessment?.featureScores?.reduce((a, b) => a + b.score, 0) / (riskAssessment?.featureScores?.length || 1) || 0 | 0}%</div>
              <Progress value={riskAssessment?.featureScores?.reduce((a, b) => a + b.score, 0) / (riskAssessment?.featureScores?.length || 1) || 0} className="mt-4 h-2" />
            </CardContent>
          </Card>

          <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Demo Readiness</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" style={{ color: "#35C98A" }} />
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-white">{project.demoReadiness || 0}%</div>
              <Progress value={project.demoReadiness || 0} className="mt-4 h-2" />
              <p className="text-sm text-muted-foreground mt-1">
                {project.demoReadiness && project.demoReadiness > 80 ? "Ready for demo" : "Needs stabilization"}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Charts & Activity */}
          <div className="lg:col-span-2 space-y-6">
            {/* Project Health Chart */}
            <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Project Health
                  <span className="text-sm text-muted-foreground">Last 30 days</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-end justify-center gap-4 px-2">
                  {[
                    { label: "Mon", score: 45, issues: 12 },
                    { label: "Tue", score: 52, issues: 8 },
                    { label: "Wed", score: 48, issues: 10 },
                    { label: "Thu", score: 61, issues: 5 },
                    { label: "Fri", score: 58, issues: 7 },
                    { label: "Sat", score: 72, issues: 3 },
                    { label: "Sun", score: demoSurvivalScore, issues: project.criticalIssues || 0 },
                  ].map((day, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-2 max-w-[60px]">
                      <div className="w-full flex-1 flex items-end justify-center">
                        <div
                          className="w-full rounded-t transition-all hover:opacity-80"
                          style={{
                            backgroundColor: "#8B7CFF",
                            height: `${Math.max(day.score, 5)}%`,
                            minHeight: "20px",
                          }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground">{day.label}</span>
                      <span className="text-xs font-medium text-white">{day.score}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Risk Distribution */}
            <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
              <CardHeader>
                <CardTitle>Risk Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {["critical", "high", "medium", "low"].map((level) => {
                    const count = riskAssessment?.riskDistribution?.[level] || 0;
                    return (
                      <div key={level} className="flex items-center gap-4">
                        <Badge variant="outline" className={cn("w-20 justify-start", riskColors[level])}>
                          {riskLabels[level]}
                        </Badge>
                        <div className="flex-1 h-2 bg-lms-background-elevated rounded-full overflow-hidden" style={{ backgroundColor: "#191F2B" }}>
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              backgroundColor: riskColors[level],
                              width: `${riskAssessment ? (count / Math.max(...Object.values(riskAssessment.riskDistribution), 1)) * 100 : 0}%`,
                            }}
                          />
                        </div>
                        <span className="text-sm font-medium text-white w-10 text-right">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Recent Activity
                  <Button variant="ghost" size="sm">View All</Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-4">
                    {recentActivity.map((activity) => (
                      <div key={activity.id} className="flex items-center gap-4 p-3 rounded-lg hover:bg-lms-background-elevated transition-colors" style={{ backgroundColor: "#191F2B" }}>
                        <div className={cn("flex h-8 w-8 items-center justify-center rounded-lg", {
                          "bg-blue-500/20": activity.type === "scan",
                          "bg-purple-500/20": activity.type === "patch",
                          "bg-green-500/20": activity.type === "test",
                          "bg-cyan-500/20": activity.type === "demo",
                          "bg-orange-500/20": activity.type === "risk",
                        })}>
                          {activity.type === "scan" && <Activity className="h-4 w-4" style={{ color: "#36C8F0" }} />}
                          {activity.type === "patch" && <Wrench className="h-4 w-4" style={{ color: "#8B7CFF" }} />}
                          {activity.type === "test" && <TestTube2 className="h-4 w-4" style={{ color: "#35C98A" }} />}
                          {activity.type === "demo" && <Monitor className="h-4 w-4" style={{ color: "#36C8F0" }} />}
                          {activity.type === "risk" && <Shield className="h-4 w-4" style={{ color: "#F5B94C" }} />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white">{activity.action}</p>
                          <p className="text-xs text-muted-foreground">{activity.entity}</p>
                        </div>
                        <span className="text-xs text-muted-foreground whitespace-nowrap">{activity.time}</span>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Issues & Actions */}
          <div className="space-y-6">
            {/* Critical Issues */}
            <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Critical Issues
                  <Badge variant="outline" className={riskColors.critical}>{criticalIssues.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  {criticalIssues.length > 0 ? (
                    <div className="space-y-3">
                      {criticalIssues.map((issue) => (
                        <div key={issue.featureId} className="p-3 rounded-lg border-l-4" style={{ borderColor: riskColors[issue.riskLevel], backgroundColor: "#191F2B" }}>
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-white truncate">{issue.featureName}</p>
                              <p className="text-xs text-muted-foreground mt-1">{issue.factors[0]?.description || "High risk detected"}</p>
                            </div>
                            <Badge variant="outline" className={riskColors[issue.riskLevel]}>{riskLabels[issue.riskLevel]}</Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
                      <CheckCircle className="h-12 w-12 mb-4" style={{ color: "#35C98A" }} />
                      <p className="text-sm">No critical issues detected</p>
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Recommended Actions */}
            <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
              <CardHeader>
                <CardTitle>Recommended Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recommendedActions.map((action) => (
                    <Link key={action.id} href={action.href} className="flex items-center justify-between p-3 rounded-lg hover:bg-lms-background-elevated transition-colors group" style={{ backgroundColor: "#191F2B" }}>
                      <div className="flex items-center gap-3">
                        <div className={cn("h-8 w-8 rounded-lg flex items-center justify-center", {
                          "bg-red-500/20": action.priority === "critical",
                          "bg-orange-500/20": action.priority === "high",
                          "bg-yellow-500/20": action.priority === "medium",
                        })}>
                          {action.priority === "critical" && <AlertTriangle className="h-4 w-4" style={{ color: "#F16C78" }} />}
                          {action.priority === "high" && <Target className="h-4 w-4" style={{ color: "#F5B94C" }} />}
                          {action.priority === "medium" && <Wrench className="h-4 w-4" style={{ color: "#36C8F0" }} />}
                        </div>
                        <div>
                          <p className="font-medium text-white text-sm">{action.title}</p>
                          <Badge variant="outline" className={cn("text-xs", {
                            "bg-red-500/20 text-red-400": action.priority === "critical",
                            "bg-orange-500/20 text-orange-400": action.priority === "high",
                            "bg-yellow-500/20 text-yellow-400": action.priority === "medium",
                          })}>
                            {action.priority}
                          </Badge>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Navigation */}
            <Card style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
              <CardHeader>
                <CardTitle>Quick Navigation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { icon: Brain, label: "AI Intelligence", href: "/intelligence", color: "#8B7CFF" },
                    { icon: Wrench, label: "Stabilization", href: "/stabilization", color: "#36C8F0" },
                    { icon: Monitor, label: "Demo Mode", href: "/demo-mode", color: "#35C98A" },
                    { icon: Shield, label: "Risk Monitor", href: "/risk-monitor", color: "#F5B94C" },
                    { icon: TestTube2, label: "Testing", href: "/testing", color: "#F16C78" },
                    { icon: FileText, label: "Demo Script", href: "/demo-script", color: "#8B7CFF" },
                  ].map((item) => (
                    <Link key={item.label} href={item.href} className="flex flex-col items-center gap-2 p-4 rounded-lg text-center hover:bg-lms-background-elevated transition-colors group" style={{ backgroundColor: "#191F2B" }}>
                      <div className="h-10 w-10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform" style={{ backgroundColor: `${item.color}20` }}>
                        <item.icon className="h-5 w-5" style={{ color: item.color }} />
                      </div>
                      <span className="text-sm font-medium text-white">{item.label}</span>
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}