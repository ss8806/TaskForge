/**
 * Zodスキーマ定義
 * フォーム検証用
 */
import { z } from 'zod';

// タスクステータス
export const taskStatusSchema = z.enum(['todo', 'doing', 'done']);

// タスク優先度
export const taskPrioritySchema = z.number().min(1).max(3);

// タスク作成スキーマ
export const taskCreateSchema = z.object({
  title: z
    .string()
    .min(1, 'タイトルは必須です')
    .max(200, 'タイトルは200文字以内で入力してください'),
  description: z
    .string()
    .max(2000, '説明は2000文字以内で入力してください')
    .optional()
    .nullable(),
  status: taskStatusSchema.default('todo'),
  priority: taskPrioritySchema.default(2),
  start_date: z.string().datetime().optional().nullable(),
  end_date: z.string().datetime().optional().nullable(),
  estimate: z.number().min(0).max(1000).optional().nullable(),
  sprint_id: z.number().optional().nullable(),
});

// タスク更新スキーマ
export const taskUpdateSchema = taskCreateSchema.partial();

// プロジェクト作成スキーマ
export const projectCreateSchema = z.object({
  name: z
    .string()
    .min(1, 'プロジェクト名は必須です')
    .max(100, 'プロジェクト名は100文字以内で入力してください'),
  description: z
    .string()
    .max(2000, '説明は2000文字以内で入力してください')
    .optional()
    .nullable(),
});

// プロジェクト更新スキーマ
export const projectUpdateSchema = projectCreateSchema.partial();

// スプリント作成スキーマ
export const sprintCreateSchema = z.object({
  name: z
    .string()
    .min(1, 'スプリント名は必須です')
    .max(100, 'スプリント名は100文字以内で入力してください'),
  start_date: z.string().datetime().optional().nullable(),
  end_date: z.string().datetime().optional().nullable(),
});

// スプリント更新スキーマ
export const sprintUpdateSchema = sprintCreateSchema.partial();

// AI分解リクエストスキーマ
export const aiDecompositionSchema = z.object({
  prompt: z
    .string()
    .min(10, '要件は10文字以上で入力してください')
    .max(5000, '要件は5000文字以内で入力してください'),
  sprint_id: z.number().optional().nullable(),
});

// ログインスキーマ
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'メールアドレスは必須です')
    .email('有効なメールアドレスを入力してください'),
  password: z
    .string()
    .min(8, 'パスワードは8文字以上で入力してください')
    .max(100, 'パスワードは100文字以内で入力してください'),
});

// 登録スキーマ
export const registerSchema = z.object({
  email: z
    .string()
    .min(1, 'メールアドレスは必須です')
    .email('有効なメールアドレスを入力してください'),
  password: z
    .string()
    .min(8, 'パスワードは8文字以上で入力してください')
    .max(100, 'パスワードは100文字以内で入力してください')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'パスワードは大文字、小文字、数字を含める必要があります'
    ),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'パスワードが一致しません',
  path: ['confirmPassword'],
});

// 型定義のエクスポート
export type TaskCreateInput = z.infer<typeof taskCreateSchema>;
export type TaskUpdateInput = z.infer<typeof taskUpdateSchema>;
export type ProjectCreateInput = z.infer<typeof projectCreateSchema>;
export type ProjectUpdateInput = z.infer<typeof projectUpdateSchema>;
export type SprintCreateInput = z.infer<typeof sprintCreateSchema>;
export type SprintUpdateInput = z.infer<typeof sprintUpdateSchema>;
export type AIDecompositionInput = z.infer<typeof aiDecompositionSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
