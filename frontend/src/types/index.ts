// ── 共通型定義 ─────────────────────────────────────────────────────────────

export interface User {
    id: number;
    email: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

// ── Project ──────────────────────────────────────────────────────────────────

export interface Project {
    id: number;
    name: string;
    description: string | null;
    owner_id: number;
    created_at: string;
    updated_at: string;
}

export interface ProjectCreate {
    name: string;
    description?: string;
}

// ── Sprint ───────────────────────────────────────────────────────────────────

export interface Sprint {
    id: number;
    name: string;
    project_id: number;
    start_date: string | null;
    end_date: string | null;
    created_at: string;
    updated_at: string;
}

export interface SprintCreate {
    name: string;
    start_date?: string;
    end_date?: string;
}

// ── Task ─────────────────────────────────────────────────────────────────────

export type TaskStatus = 'todo' | 'doing' | 'done';
export type TaskPriority = 1 | 2 | 3;

export interface Task {
    id: number;
    project_id: number;
    sprint_id: number | null;
    title: string;
    description: string | null;
    status: TaskStatus;
    priority: TaskPriority;
    start_date: string | null;
    end_date: string | null;
    estimate: number | null;
    created_at: string;
    updated_at: string;
}

export interface TaskCreate {
    title: string;
    description?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    start_date?: string;
    end_date?: string;
    estimate?: number;
    sprint_id?: number;
}

export interface TaskUpdate {
    title?: string;
    description?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    start_date?: string;
    end_date?: string;
    estimate?: number;
    sprint_id?: number | null;
}
