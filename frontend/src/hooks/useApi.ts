"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, apiEndpoints } from "@/lib/api";
import { useAppStore } from "@/store";
import type { Project, Team, ScanSession, RiskAssessment, Feature, TestExecution, DemoConfiguration, DemoScript, Notification, GitCommit, PaginatedResponse } from "@/types";

export function useProjects(teamId?: string) {
  return useQuery({
    queryKey: ["projects", teamId],
    queryFn: async () => {
      const params = teamId ? `?team_id=${teamId}` : "";
      const response = await api.get<PaginatedResponse<Project>>(`${apiEndpoints.projects.list}${params}`);
      return response.data;
    },
    enabled: !!teamId,
  });
}

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ["project", projectId],
    queryFn: async () => {
      const response = await api.get<Project>(apiEndpoints.projects.get(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  const { currentTeam } = useAppStore();
  
  return useMutation({
    mutationFn: async (data: Partial<Project>) => {
      const response = await api.post<Project>(apiEndpoints.projects.create, {
        ...data,
        team_id: currentTeam?.id,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", currentTeam?.id] });
    },
  });
}

export function useScanProject() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (projectId: string) => {
      const response = await api.post<ScanSession>(apiEndpoints.projects.scan(projectId));
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["project", data.project_id] });
      queryClient.invalidateQueries({ queryKey: ["scan", data.id] });
    },
  });
}

export function useScanSession(scanId: string) {
  return useQuery({
    queryKey: ["scan", scanId],
    queryFn: async () => {
      const response = await api.get<ScanSession>(apiEndpoints.scanner.status(scanId));
      return response.data;
    },
    enabled: !!scanId,
    refetchInterval: (data) => data?.status === "running" ? 2000 : false,
  });
}

export function useScanResults(scanId: string) {
  return useQuery({
    queryKey: ["scan-results", scanId],
    queryFn: async () => {
      const response = await api.get(apiEndpoints.scanner.results(scanId));
      return response.data;
    },
    enabled: !!scanId,
  });
}

export function useFileTree(scanId: string) {
  return useQuery({
    queryKey: ["file-tree", scanId],
    queryFn: async () => {
      const response = await api.get(apiEndpoints.scanner.fileTree(scanId));
      return response.data;
    },
    enabled: !!scanId,
  });
}

export function useFileContent(scanId: string, path: string) {
  return useQuery({
    queryKey: ["file-content", scanId, path],
    queryFn: async () => {
      const response = await api.get(apiEndpoints.scanner.fileContent(scanId, path));
      return response.data;
    },
    enabled: !!scanId && !!path,
  });
}

export function useRiskAssessment(projectId: string) {
  return useQuery({
    queryKey: ["risk-assessment", projectId],
    queryFn: async () => {
      const response = await api.get<RiskAssessment>(apiEndpoints.intelligence.getAssessment(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useAnalyzeProject() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (projectId: string) => {
      const response = await api.post<RiskAssessment>(apiEndpoints.intelligence.analyze(projectId));
      return response.data;
    },
    onSuccess: (data, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["risk-assessment", projectId] });
      queryClient.invalidateQueries({ queryKey: ["feature-graph", projectId] });
      queryClient.invalidateQueries({ queryKey: ["happy-paths", projectId] });
      queryClient.invalidateQueries({ queryKey: ["recommendations", projectId] });
    },
  });
}

export function useFeatureGraph(projectId: string) {
  return useQuery({
    queryKey: ["feature-graph", projectId],
    queryFn: async () => {
      const response = await api.get(apiEndpoints.intelligence.featureGraph(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useHappyPaths(projectId: string) {
  return useQuery({
    queryKey: ["happy-paths", projectId],
    queryFn: async () => {
      const response = await api.get(apiEndpoints.intelligence.happyPaths(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useAIRecommendations(projectId: string) {
  return useQuery({
    queryKey: ["recommendations", projectId],
    queryFn: async () => {
      const response = await api.get(apiEndpoints.intelligence.recommendations(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useStabilizationTasks(projectId: string) {
  return useQuery({
    queryKey: ["stabilization-tasks", projectId],
    queryFn: async () => {
      const response = await api.get(apiEndpoints.stabilization.tasks(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useCreateStabilizationTask() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, data }: { projectId: string; data: any }) => {
      const response = await api.post(apiEndpoints.stabilization.createTask(projectId), data);
      return response.data;
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["stabilization-tasks", projectId] });
    },
  });
}

export function useApprovePatch() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, taskId, patchId }: { projectId: string; taskId: string; patchId: string }) => {
      const response = await api.post(apiEndpoints.stabilization.approvePatch(projectId, taskId, patchId));
      return response.data;
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["stabilization-tasks", projectId] });
    },
  });
}

export function useApplyPatches() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, taskId }: { projectId: string; taskId: string }) => {
      const response = await api.post(apiEndpoints.stabilization.applyPatches(projectId, taskId));
      return response.data;
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["stabilization-tasks", projectId] });
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
    },
  });
}

export function useRollbackTask() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, taskId }: { projectId: string; taskId: string }) => {
      const response = await api.post(apiEndpoints.stabilization.rollback(projectId, taskId));
      return response.data;
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["stabilization-tasks", projectId] });
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
    },
  });
}

export function useTestExecutions(projectId: string) {
  return useQuery({
    queryKey: ["test-executions", projectId],
    queryFn: async () => {
      const response = await api.get<TestExecution[]>(apiEndpoints.testing.listExecutions(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useRunTests() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, type }: { projectId: string; type?: string }) => {
      const response = await api.post<TestExecution>(apiEndpoints.testing.run(projectId), { type });
      return response.data;
    },
    onSuccess: (data, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["test-executions", projectId] });
      queryClient.invalidateQueries({ queryKey: ["test-execution", data.id] });
    },
  });
}

export function useTestExecution(projectId: string, executionId: string) {
  return useQuery({
    queryKey: ["test-execution", executionId],
    queryFn: async () => {
      const response = await api.get<TestExecution>(apiEndpoints.testing.getExecution(projectId, executionId));
      return response.data;
    },
    enabled: !!projectId && !!executionId,
    refetchInterval: (data) => data?.status === "running" ? 3000 : false,
  });
}

export function useRetryTest() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, executionId }: { projectId: string; executionId: string }) => {
      const response = await api.post(apiEndpoints.testing.retry(projectId, executionId));
      return response.data;
    },
    onSuccess: (_, { projectId, executionId }) => {
      queryClient.invalidateQueries({ queryKey: ["test-executions", projectId] });
      queryClient.invalidateQueries({ queryKey: ["test-execution", executionId] });
    },
  });
}

export function useDemoConfig(projectId: string) {
  return useQuery({
    queryKey: ["demo-config", projectId],
    queryFn: async () => {
      const response = await api.get<DemoConfiguration>(apiEndpoints.demo.config(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useUpdateDemoConfig() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, config }: { projectId: string; config: Partial<DemoConfiguration> }) => {
      const response = await api.put<DemoConfiguration>(apiEndpoints.demo.updateConfig(projectId), config);
      return response.data;
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["demo-config", projectId] });
    },
  });
}

export function useActivateDemo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (projectId: string) => {
      const response = await api.post(apiEndpoints.demo.activate(projectId));
      return response.data;
    },
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["demo-config", projectId] });
      queryClient.invalidateQueries({ queryKey: ["demo-status", projectId] });
    },
  });
}

export function useDeactivateDemo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (projectId: string) => {
      const response = await api.post(apiEndpoints.demo.deactivate(projectId));
      return response.data;
    },
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["demo-config", projectId] });
      queryClient.invalidateQueries({ queryKey: ["demo-status", projectId] });
    },
  });
}

export function useDemoStatus(projectId: string) {
  return useQuery({
    queryKey: ["demo-status", projectId],
    queryFn: async () => {
      const response = await api.get(apiEndpoints.demo.status(projectId));
      return response.data;
    },
    enabled: !!projectId,
    refetchInterval: 5000,
  });
}

export function useDemoScript(projectId: string) {
  return useQuery({
    queryKey: ["demo-script", projectId],
    queryFn: async () => {
      const response = await api.get<DemoScript>(apiEndpoints.demoScript.get(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useGenerateDemoScript() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, options }: { projectId: string; options: { duration: number; audience: string } }) => {
      const response = await api.post<DemoScript>(apiEndpoints.demoScript.generate(projectId), options);
      return response.data;
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["demo-script", projectId] });
    },
  });
}

export function useGitCommits(projectId: string) {
  return useQuery({
    queryKey: ["git-commits", projectId],
    queryFn: async () => {
      const response = await api.get<GitCommit[]>(apiEndpoints.risk.commits(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });
}

export function useAnalyzeCommit() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ projectId, sha }: { projectId: string; sha: string }) => {
      const response = await api.post(apiEndpoints.risk.analyzeCommit(projectId, sha));
      return response.data;
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["git-commits", projectId] });
    },
  });
}

export function useFreezeDemo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (projectId: string) => {
      const response = await api.post(apiEndpoints.risk.freeze(projectId));
      return response.data;
    },
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["git-commits", projectId] });
    },
  });
}

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      const response = await api.get<Notification[]>(apiEndpoints.notifications.list);
      return response.data;
    },
    refetchInterval: 30000,
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await api.post(apiEndpoints.notifications.markRead(id));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

export function useTeams() {
  return useQuery({
    queryKey: ["teams"],
    queryFn: async () => {
      const response = await api.get<Team[]>(apiEndpoints.teams.list);
      return response.data;
    },
  });
}

export function useCreateTeam() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: { name: string; description?: string }) => {
      const response = await api.post<Team>(apiEndpoints.teams.create, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
    },
  });
}