"use client";

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { Project, Team, User, ScanSession, RiskAssessment, Feature, TestExecution, DemoConfiguration, DemoScript, Notification, GitCommit } from "@/types";

interface AppState {
  // User & Auth
  user: User | null;
  setUser: (user: User | null) => void;
  
  // Current context
  currentTeam: Team | null;
  setCurrentTeam: (team: Team | null) => void;
  currentProject: Project | null;
  setCurrentProject: (project: Project | null) => void;
  
  // Projects
  projects: Project[];
  setProjects: (projects: Project[]) => void;
  addProject: (project: Project) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  removeProject: (id: string) => void;
  
  // Teams
  teams: Team[];
  setTeams: (teams: Team[]) => void;
  addTeam: (team: Team) => void;
  updateTeam: (id: string, updates: Partial<Team>) => void;
  
  // Scanning
  scanSession: ScanSession | null;
  setScanSession: (session: ScanSession | null) => void;
  updateScanProgress: (progress: number, step: string) => void;
  
  // Intelligence
  riskAssessment: RiskAssessment | null;
  setRiskAssessment: (assessment: RiskAssessment | null) => void;
  features: Feature[];
  setFeatures: (features: Feature[]) => void;
  updateFeature: (id: string, updates: Partial<Feature>) => void;
  
  // Stabilization
  stabilizationTasks: Record<string, any[]>;
  setStabilizationTasks: (projectId: string, tasks: any[]) => void;
  addStabilizationTask: (projectId: string, task: any) => void;
  updateStabilizationTask: (projectId: string, taskId: string, updates: any) => void;
  
  // Testing
  testExecutions: TestExecution[];
  setTestExecutions: (executions: TestExecution[]) => void;
  addTestExecution: (execution: TestExecution) => void;
  updateTestExecution: (id: string, updates: Partial<TestExecution>) => void;
  
  // Demo
  demoConfig: DemoConfiguration | null;
  setDemoConfig: (config: DemoConfiguration | null) => void;
  demoScript: DemoScript | null;
  setDemoScript: (script: DemoScript | null) => void;
  
  // Risk Monitor
  gitCommits: GitCommit[];
  setGitCommits: (commits: GitCommit[]) => void;
  addGitCommit: (commit: GitCommit) => void;
  demoFrozen: boolean;
  setDemoFrozen: (frozen: boolean) => void;
  
  // Notifications
  notifications: Notification[];
  setNotifications: (notifications: Notification[]) => void;
  addNotification: (notification: Notification) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  unreadCount: number;
  
  // UI State
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  
  // Loading states
  globalLoading: boolean;
  setGlobalLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // User & Auth
      user: null,
      setUser: (user) => set({ user }),
      
      // Current context
      currentTeam: null,
      setCurrentTeam: (team) => set({ currentTeam: team }),
      currentProject: null,
      setCurrentProject: (project) => set({ currentProject: project }),
      
      // Projects
      projects: [],
      setProjects: (projects) => set({ projects }),
      addProject: (project) => set((state) => ({ projects: [project, ...state.projects] })),
      updateProject: (id, updates) => set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? { ...p, ...updates } : p)),
        currentProject: state.currentProject?.id === id ? { ...state.currentProject, ...updates } : state.currentProject,
      })),
      removeProject: (id) => set((state) => ({
        projects: state.projects.filter((p) => p.id !== id),
        currentProject: state.currentProject?.id === id ? null : state.currentProject,
      })),
      
      // Teams
      teams: [],
      setTeams: (teams) => set({ teams }),
      addTeam: (team) => set((state) => ({ teams: [team, ...state.teams] })),
      updateTeam: (id, updates) => set((state) => ({
        teams: state.teams.map((t) => (t.id === id ? { ...t, ...updates } : t)),
        currentTeam: state.currentTeam?.id === id ? { ...state.currentTeam, ...updates } : state.currentTeam,
      })),
      
      // Scanning
      scanSession: null,
      setScanSession: (session) => set({ scanSession: session }),
      updateScanProgress: (progress, step) => set((state) => ({
        scanSession: state.scanSession ? { ...state.scanSession, progress, currentStep: step } : null,
      })),
      
      // Intelligence
      riskAssessment: null,
      setRiskAssessment: (assessment) => set({ riskAssessment: assessment }),
      features: [],
      setFeatures: (features) => set({ features }),
      updateFeature: (id, updates) => set((state) => ({
        features: state.features.map((f) => (f.id === id ? { ...f, ...updates } : f)),
      })),
      
      // Stabilization
      stabilizationTasks: {},
      setStabilizationTasks: (projectId, tasks) => set((state) => ({
        stabilizationTasks: { ...state.stabilizationTasks, [projectId]: tasks },
      })),
      addStabilizationTask: (projectId, task) => set((state) => ({
        stabilizationTasks: {
          ...state.stabilizationTasks,
          [projectId]: [task, ...(state.stabilizationTasks[projectId] || [])],
        },
      })),
      updateStabilizationTask: (projectId, taskId, updates) => set((state) => ({
        stabilizationTasks: {
          ...state.stabilizationTasks,
          [projectId]: (state.stabilizationTasks[projectId] || []).map((t) =>
            t.id === taskId ? { ...t, ...updates } : t
          ),
        },
      })),
      
      // Testing
      testExecutions: [],
      setTestExecutions: (executions) => set({ testExecutions: executions }),
      addTestExecution: (execution) => set((state) => ({
        testExecutions: [execution, ...state.testExecutions],
      })),
      updateTestExecution: (id, updates) => set((state) => ({
        testExecutions: state.testExecutions.map((e) => (e.id === id ? { ...e, ...updates } : e)),
      })),
      
      // Demo
      demoConfig: null,
      setDemoConfig: (config) => set({ demoConfig: config }),
      demoScript: null,
      setDemoScript: (script) => set({ demoScript: script }),
      
      // Risk Monitor
      gitCommits: [],
      setGitCommits: (commits) => set({ gitCommits: commits }),
      addGitCommit: (commit) => set((state) => ({ gitCommits: [commit, ...state.gitCommits] })),
      demoFrozen: false,
      setDemoFrozen: (frozen) => set({ demoFrozen: frozen }),
      
      // Notifications
      notifications: [],
      setNotifications: (notifications) => set({ 
        notifications,
        unreadCount: notifications.filter((n) => !n.read).length,
      }),
      addNotification: (notification) => set((state) => ({
        notifications: [notification, ...state.notifications],
        unreadCount: state.unreadCount + (notification.read ? 0 : 1),
      })),
      markNotificationRead: (id) => set((state) => ({
        notifications: state.notifications.map((n) =>
          n.id === id ? { ...n, read: true } : n
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      })),
      markAllNotificationsRead: () => set((state) => ({
        notifications: state.notifications.map((n) => ({ ...n, read: true })),
        unreadCount: 0,
      })),
      unreadCount: 0,
      
      // UI State
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      // Loading states
      globalLoading: false,
      setGlobalLoading: (loading) => set({ globalLoading: loading }),
    }),
    {
      name: "lms-app-storage",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        currentTeam: state.currentTeam,
        currentProject: state.currentProject,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
);