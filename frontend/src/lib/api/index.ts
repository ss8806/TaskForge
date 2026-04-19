import type {
  Project,
  ProjectCreate,
  Sprint,
  SprintCreate,
  Task,
  TaskCreate,
  TaskUpdate,
  TokenResponse,
} from "@/types";

export interface RepositoryCreate {
  url: string;
  repo_type?: string;
  branch?: string;
}

export interface RepositoryResponse {
  id: number;
  project_id: number;
  url: string;
  repo_type: string;
  branch: string;
  analysis_result: Record<string, unknown> | null;
  last_analyzed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResultResponse {
  structure: Record<string, unknown> | null;
  tech_stack: string[];
  api_endpoints: Array<Record<string, string>>;
  database_models: Array<Record<string, string>>;
  existing_features: string[];
  last_analyzed_at: string | null;
}

import { apiFetch } from "./fetch-client";

// ── Auth ────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (email: string, password: string) =>
    apiFetch<TokenResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  login: (email: string, password: string) =>
    apiFetch<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
};

// ── Projects ─────────────────────────────────────────────────────────────────

export const projectsApi = {
  list: (page = 1, page_size = 20) =>
    apiFetch<{ items: Project[]; total: number; page: number; page_size: number; total_pages: number }>("/api/projects", { params: { page, page_size } }).then(res => res.items),
  create: (data: ProjectCreate) =>
    apiFetch<Project>("/api/projects", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  get: (id: number) => apiFetch<Project>(`/api/projects/${id}`),
  delete: (id: number) =>
    apiFetch<void>(`/api/projects/${id}`, { method: "DELETE" }),
};

// ── Sprints ───────────────────────────────────────────────────────────────────

export const sprintsApi = {
  list: (projectId: number) =>
    apiFetch<Sprint[]>(`/api/projects/${projectId}/sprints`),
  create: (projectId: number, data: SprintCreate) =>
    apiFetch<Sprint>(`/api/projects/${projectId}/sprints`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (projectId: number, sprintId: number, data: SprintCreate) =>
    apiFetch<Sprint>(`/api/projects/${projectId}/sprints/${sprintId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (projectId: number, sprintId: number) =>
    apiFetch<void>(`/api/projects/${projectId}/sprints/${sprintId}`, {
      method: "DELETE",
    }),
};

// ── Tasks ─────────────────────────────────────────────────────────────────────

export const tasksApi = {
  list: (
    projectId: number,
    params?: {
      status?: string;
      sprint_id?: number;
      page?: number;
      page_size?: number;
    }
  ) =>
    apiFetch<{ items: Task[]; total: number; page: number; page_size: number; total_pages: number }>(
      `/api/projects/${projectId}/tasks`,
      { params }
    ).then((res) => res.items),
  create: (projectId: number, data: TaskCreate) =>
    apiFetch<Task>(`/api/projects/${projectId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (taskId: number, data: TaskUpdate) =>
    apiFetch<Task>(`/api/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (taskId: number) =>
    apiFetch<void>(`/api/tasks/${taskId}`, { method: "DELETE" }),
};

// ── AI ────────────────────────────────────────────────────────────────────────

interface AIDecomposeResponse {
  tasks: Array<{
    title: string;
    description?: string;
    status?: string;
    priority?: number;
    estimate?: number;
  }>;
}

export const aiApi = {
  decompose: (projectId: number, prompt: string, sprintId?: number) =>
    apiFetch<AIDecomposeResponse>(`/api/projects/${projectId}/ai/decompose`, {
      method: "POST",
      body: JSON.stringify({ prompt, sprint_id: sprintId }),
    }),
};

// ── Repositories ──────────────────────────────────────────────────────────────

export const repositoriesApi = {
  register: (projectId: number, data: RepositoryCreate) =>
    apiFetch<RepositoryResponse>(`/api/projects/${projectId}/repositories`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  analyze: (projectId: number) =>
    apiFetch<{ status: string; result: Record<string, unknown>; last_analyzed_at: string }>(
      `/api/projects/${projectId}/repositories/analyze`,
      { method: "POST" }
    ),

  getAnalysis: (projectId: number) =>
    apiFetch<AnalysisResultResponse>(`/api/projects/${projectId}/repositories/analysis`),

  get: (projectId: number) =>
    apiFetch<RepositoryResponse>(`/api/projects/${projectId}/repositories`),

  delete: (projectId: number) =>
    apiFetch<void>(`/api/projects/${projectId}/repositories`, { method: "DELETE" }),
};
