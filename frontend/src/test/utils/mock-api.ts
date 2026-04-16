"""APIモックユーティリティ for testing."""
import { describe, vi, beforeEach, afterEach } from 'vitest';

// グローバルのfetchをモック
global.fetch = vi.fn();

// モックデータの型定義
export type MockTask = {
  id: number;
  project_id: number;
  sprint_id: number | null;
  title: string;
  description: string | null;
  status: 'todo' | 'doing' | 'done';
  priority: number;
  start_date: string | null;
  end_date: string | null;
  estimate: number | null;
  created_at: string;
  updated_at: string;
};

export type MockProject = {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  created_at: string;
  updated_at: string;
};

export type MockSprint = {
  id: number;
  name: string;
  project_id: number;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
};

// テスト用のモックデータ
export const mockTasks: MockTask[] = [
  {
    id: 1,
    project_id: 1,
    sprint_id: null,
    title: 'Test Task 1',
    description: 'A test task',
    status: 'todo',
    priority: 2,
    start_date: null,
    end_date: null,
    estimate: 4.0,
    created_at: '2026-03-24T00:00:00Z',
    updated_at: '2026-03-24T00:00:00Z',
  },
  {
    id: 2,
    project_id: 1,
    sprint_id: 1,
    title: 'Test Task 2',
    description: 'Another test task',
    status: 'doing',
    priority: 3,
    start_date: null,
    end_date: null,
    estimate: 6.0,
    created_at: '2026-03-24T00:00:00Z',
    updated_at: '2026-03-24T00:00:00Z',
  },
  {
    id: 3,
    project_id: 1,
    sprint_id: 1,
    title: 'Test Task 3',
    description: 'Completed task',
    status: 'done',
    priority: 1,
    start_date: null,
    end_date: null,
    estimate: 2.0,
    created_at: '2026-03-24T00:00:00Z',
    updated_at: '2026-03-24T00:00:00Z',
  },
];

export const mockProjects: MockProject[] = [
  {
    id: 1,
    name: 'Test Project',
    description: 'A test project',
    owner_id: 1,
    created_at: '2026-03-24T00:00:00Z',
    updated_at: '2026-03-24T00:00:00Z',
  },
];

export const mockSprints: MockSprint[] = [
  {
    id: 1,
    name: 'Sprint 1',
    project_id: 1,
    start_date: '2026-03-24T00:00:00Z',
    end_date: '2026-04-07T00:00:00Z',
    created_at: '2026-03-24T00:00:00Z',
    updated_at: '2026-03-24T00:00:00Z',
  },
];

// fetchのモックヘルパー
export function mockFetchSuccess(data: unknown, status = 200) {
  return vi.fn().mockResolvedValue({
    ok: true,
    status,
    json: async () => data,
  } as Response);
}

export function mockFetchError(status = 500, message = 'Internal Server Error') {
  return vi.fn().mockResolvedValue({
    ok: false,
    status,
    json: async () => ({ detail: message }),
  } as Response);
}

// 各テストの後にモックをリセット
export function resetMocks() {
  vi.clearAllMocks();
}
