import apiClient from './client';
import type {
    TokenResponse,
    Project,
    ProjectCreate,
    Sprint,
    SprintCreate,
    Task,
    TaskCreate,
    TaskUpdate,
} from '@/types';

// ── Auth ────────────────────────────────────────────────────────────────────

export const authApi = {
    register: (email: string, password: string) =>
        apiClient.post<TokenResponse>('/api/auth/register', { email, password }),
    login: (email: string, password: string) =>
        apiClient.post<TokenResponse>('/api/auth/login', { email, password }),
};

// ── Projects ─────────────────────────────────────────────────────────────────

export const projectsApi = {
    list: (limit = 20, offset = 0) =>
        apiClient.get<Project[]>('/api/projects', { params: { limit, offset } }),
    create: (data: ProjectCreate) =>
        apiClient.post<Project>('/api/projects', data),
    get: (id: number) =>
        apiClient.get<Project>(`/api/projects/${id}`),
    delete: (id: number) =>
        apiClient.delete(`/api/projects/${id}`),
};

// ── Sprints ───────────────────────────────────────────────────────────────────

export const sprintsApi = {
    list: (projectId: number) =>
        apiClient.get<Sprint[]>(`/api/projects/${projectId}/sprints`),
    create: (projectId: number, data: SprintCreate) =>
        apiClient.post<Sprint>(`/api/projects/${projectId}/sprints`, data),
    update: (projectId: number, sprintId: number, data: SprintCreate) =>
        apiClient.put<Sprint>(`/api/projects/${projectId}/sprints/${sprintId}`, data),
    delete: (projectId: number, sprintId: number) =>
        apiClient.delete(`/api/projects/${projectId}/sprints/${sprintId}`),
};

// ── Tasks ─────────────────────────────────────────────────────────────────────

export const tasksApi = {
    list: (
        projectId: number,
        params?: { status?: string; sprint_id?: number; limit?: number; offset?: number }
    ) =>
        apiClient.get<Task[]>(`/api/projects/${projectId}/tasks`, { params }),
    create: (projectId: number, data: TaskCreate) =>
        apiClient.post<Task>(`/api/projects/${projectId}/tasks`, data),
    update: (taskId: number, data: TaskUpdate) =>
        apiClient.put<Task>(`/api/tasks/${taskId}`, data),
    delete: (taskId: number) =>
        apiClient.delete(`/api/tasks/${taskId}`),
};

// ── AI ────────────────────────────────────────────────────────────────────────

export const aiApi = {
    decompose: (projectId: number, prompt: string) =>
        apiClient.post<{ tasks: any[] }>(`/api/projects/${projectId}/ai/decompose`, { prompt }),
};
