import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getAccessToken, setTokens, clearTokens } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token: newRefreshToken } = response.data;
          setTokens(access_token, newRefreshToken);
          
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        }
      } catch {
        clearTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }
    }

    return Promise.reject(error);
  }
);

function getRefreshToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("refresh_token");
  }
  return null;
}

export const apiEndpoints = {
  auth: {
    login: "/auth/login",
    register: "/auth/register",
    logout: "/auth/logout",
    refresh: "/auth/refresh",
    me: "/auth/me",
    github: "/auth/github",
    githubCallback: "/auth/github/callback",
  },
  users: {
    list: "/users",
    get: (id: string) => `/users/${id}`,
    update: (id: string) => `/users/${id}`,
    delete: (id: string) => `/users/${id}`,
  },
  teams: {
    list: "/teams",
    create: "/teams",
    get: (id: string) => `/teams/${id}`,
    update: (id: string) => `/teams/${id}`,
    delete: (id: string) => `/teams/${id}`,
    members: (id: string) => `/teams/${id}/members`,
    invite: (id: string) => `/teams/${id}/invite`,
    removeMember: (id: string, userId: string) => `/teams/${id}/members/${userId}`,
    updateMemberRole: (id: string, userId: string) => `/teams/${id}/members/${userId}`,
  },
  projects: {
    list: "/projects",
    create: "/projects",
    get: (id: string) => `/projects/${id}`,
    update: (id: string) => `/projects/${id}`,
    delete: (id: string) => `/projects/${id}`,
    scan: (id: string) => `/projects/${id}/scan`,
    scanStatus: (id: string) => `/projects/${id}/scan/status`,
    scanResults: (id: string) => `/projects/${id}/scan/results`,
    dashboard: (id: string) => `/projects/${id}/dashboard`,
  },
  scanner: {
    upload: "/scanner/upload",
    github: "/scanner/github",
    status: (id: string) => `/scanner/${id}/status`,
    results: (id: string) => `/scanner/${id}/results`,
    fileTree: (id: string) => `/scanner/${id}/file-tree`,
    fileContent: (id: string, path: string) => `/scanner/${id}/file-content?path=${encodeURIComponent(path)}`,
  },
  intelligence: {
    analyze: (projectId: string) => `/intelligence/${projectId}/analyze`,
    getAssessment: (projectId: string) => `/intelligence/${projectId}/assessment`,
    featureGraph: (projectId: string) => `/intelligence/${projectId}/feature-graph`,
    happyPaths: (projectId: string) => `/intelligence/${projectId}/happy-paths`,
    recommendations: (projectId: string) => `/intelligence/${projectId}/recommendations`,
  },
  stabilization: {
    tasks: (projectId: string) => `/stabilization/${projectId}/tasks`,
    createTask: (projectId: string) => `/stabilization/${projectId}/tasks`,
    getTask: (projectId: string, taskId: string) => `/stabilization/${projectId}/tasks/${taskId}`,
    approvePatch: (projectId: string, taskId: string, patchId: string) => `/stabilization/${projectId}/tasks/${taskId}/patches/${patchId}/approve`,
    rejectPatch: (projectId: string, taskId: string, patchId: string) => `/stabilization/${projectId}/tasks/${taskId}/patches/${patchId}/reject`,
    applyPatches: (projectId: string, taskId: string) => `/stabilization/${projectId}/tasks/${taskId}/apply`,
    rollback: (projectId: string, taskId: string) => `/stabilization/${projectId}/tasks/${taskId}/rollback`,
    history: (projectId: string) => `/stabilization/${projectId}/history`,
  },
  demo: {
    config: (projectId: string) => `/demo/${projectId}/config`,
    updateConfig: (projectId: string) => `/demo/${projectId}/config`,
    activate: (projectId: string) => `/demo/${projectId}/activate`,
    deactivate: (projectId: string) => `/demo/${projectId}/deactivate`,
    status: (projectId: string) => `/demo/${projectId}/status`,
    preview: (projectId: string) => `/demo/${projectId}/preview`,
    reset: (projectId: string) => `/demo/${projectId}/reset`,
  },
  risk: {
    monitor: (projectId: string) => `/risk/${projectId}/monitor`,
    commits: (projectId: string) => `/risk/${projectId}/commits`,
    freeze: (projectId: string) => `/risk/${projectId}/freeze`,
    unfreeze: (projectId: string) => `/risk/${projectId}/unfreeze`,
    analyzeCommit: (projectId: string, sha: string) => `/risk/${projectId}/commits/${sha}/analyze`,
  },
  testing: {
    run: (projectId: string) => `/testing/${projectId}/run`,
    getExecution: (projectId: string, executionId: string) => `/testing/${projectId}/executions/${executionId}`,
    listExecutions: (projectId: string) => `/testing/${projectId}/executions`,
    getReport: (projectId: string, executionId: string) => `/testing/${projectId}/executions/${executionId}/report`,
    retry: (projectId: string, executionId: string) => `/testing/${projectId}/executions/${executionId}/retry`,
  },
  demoScript: {
    generate: (projectId: string) => `/demo-script/${projectId}/generate`,
    get: (projectId: string) => `/demo-script/${projectId}`,
    update: (projectId: string) => `/demo-script/${projectId}`,
    export: (projectId: string, format: string) => `/demo-script/${projectId}/export?format=${format}`,
  },
  activity: {
    list: (projectId: string) => `/activity/${projectId}`,
    get: (projectId: string, id: string) => `/activity/${projectId}/${id}`,
  },
  notifications: {
    list: "/notifications",
    markRead: (id: string) => `/notifications/${id}/read`,
    markAllRead: "/notifications/read-all",
  },
  reports: {
    scan: (projectId: string) => `/reports/${projectId}/scan`,
    risk: (projectId: string) => `/reports/${projectId}/risk`,
    stabilization: (projectId: string) => `/reports/${projectId}/stabilization`,
    testing: (projectId: string) => `/reports/${projectId}/testing`,
    demoReadiness: (projectId: string) => `/reports/${projectId}/demo-readiness`,
    export: (projectId: string, type: string) => `/reports/${projectId}/export?type=${type}`,
  },
};

export default api;