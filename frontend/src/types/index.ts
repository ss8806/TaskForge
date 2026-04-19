// ═══════════════════════════════════════════════════════════════════════
// 手動定義の型（UI固有の型のみ）
// APIレスポンス型は generated.ts を参照
// ═══════════════════════════════════════════════════════════════════════

// 自動生成された型をエクスポート
export type {
  paths,
  components,
  operations,
} from "./generated";

// 自動生成されたスキーマ型を便利な名前で再エクスポート
import type { components } from "./generated";

export type User = components["schemas"]["UserResponse"];
export type Project = components["schemas"]["ProjectResponse"];
export type ProjectCreate = components["schemas"]["ProjectCreate"];
export type Sprint = components["schemas"]["SprintResponse"];
export type SprintCreate = components["schemas"]["SprintCreate"];
export type Task = components["schemas"]["TaskResponse"];
export type TaskCreate = components["schemas"]["TaskCreate"];
export type TaskUpdate = components["schemas"]["TaskUpdate"];
export type TokenResponse = components["schemas"]["TokenResponse"];
export type PaginatedProjects = components["schemas"]["PaginatedResponse_ProjectResponse_"];
export type PaginatedTasks = components["schemas"]["PaginatedResponse_TaskResponse_"];

// フロントエンド固有の型
export type TaskStatus = "todo" | "doing" | "done";
export type TaskPriority = 1 | 2 | 3;
