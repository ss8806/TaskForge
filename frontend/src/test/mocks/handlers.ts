import { http, HttpResponse } from "msw";
import { setupWorker } from "msw/browser";

import type { Project, Task } from "@/types";

// ハンドラー定義
export const handlers = [
  // 認証
  http.post("/api/auth/login", async ({ request }) => {
    const body = await request.json();
    const { email, password } = body as { email: string; password: string };

    if (email === "test@example.com" && password === "password123") {
      return HttpResponse.json({
        access_token: "mock-jwt-token",
        token_type: "bearer",
      });
    }

    return HttpResponse.json(
      { detail: "Incorrect email or password" },
      { status: 401 }
    );
  }),

  // プロジェクト一覧
  http.get("/api/projects", () => {
    return HttpResponse.json({
      items: [
        {
          id: 1,
          name: "Test Project",
          description: "テストプロジェクトです",
          status: "active",
          owner_id: 1,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
        } as Project,
      ] as Project[],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
      has_next: false,
      has_prev: false,
    });
  }),

  // タスク一覧
  http.get("/api/projects/:projectId/tasks", () => {
    return HttpResponse.json({
      items: [
        {
          id: 1,
          project_id: 1,
          sprint_id: null,
          title: "Test Task",
          description: "テストタスクです",
          status: "todo",
          priority: 2,
          start_date: null,
          end_date: null,
          estimate: null,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
        } as Task,
      ] as Task[],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
      has_next: false,
      has_prev: false,
    });
  }),
];

// Service Workerセットアップ
export const worker = setupWorker(...handlers);
