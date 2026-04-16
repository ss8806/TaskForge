import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TaskDetailDialog from '@/components/task-detail-dialog';
import type { Task } from '@/types';

describe('TaskDetailDialog', () => {
  let queryClient: QueryClient;
  const mockTask: Task = {
    id: 1,
    project_id: 1,
    sprint_id: 1,
    title: 'Test Task',
    description: 'A test task description',
    status: 'todo',
    priority: 2,
    start_date: null,
    end_date: null,
    estimate: 4.0,
    created_at: '2026-03-24T00:00:00Z',
    updated_at: '2026-03-24T00:00:00Z',
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  const renderWithQueryClient = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    );
  };

  it('does not render when isOpen is false', () => {
    renderWithQueryClient(
      <TaskDetailDialog
        task={mockTask}
        isOpen={false}
        onClose={vi.fn()}
        projectId={1}
      />
    );

    expect(screen.queryByText('タスク詳細')).not.toBeInTheDocument();
  });

  it('renders when isOpen is true', () => {
    const mockOnClose = vi.fn();
    renderWithQueryClient(
      <TaskDetailDialog
        task={mockTask}
        isOpen={true}
        onClose={mockOnClose}
        projectId={1}
      />
    );

    expect(screen.getByText('タスク詳細')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test Task')).toBeInTheDocument();
    expect(screen.getByDisplayValue('A test task description')).toBeInTheDocument();
  });

  it('renders all form fields with correct values', () => {
    renderWithQueryClient(
      <TaskDetailDialog
        task={mockTask}
        isOpen={true}
        onClose={vi.fn()}
        projectId={1}
      />
    );

    // タイトル
    expect(screen.getByDisplayValue('Test Task')).toBeInTheDocument();
    // 説明
    expect(screen.getByDisplayValue('A test task description')).toBeInTheDocument();
    // ステータス
    expect(screen.getByText('未着手')).toBeInTheDocument();
    // 優先度
    expect(screen.getByText('中 (Medium)')).toBeInTheDocument();
  });

  it('calls onClose when cancel button is clicked', async () => {
    const mockOnClose = vi.fn();
    renderWithQueryClient(
      <TaskDetailDialog
        task={mockTask}
        isOpen={true}
        onClose={mockOnClose}
        projectId={1}
      />
    );

    const cancelButton = screen.getByText('キャンセル');
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('disables save button when title is empty', () => {
    renderWithQueryClient(
      <TaskDetailDialog
        task={mockTask}
        isOpen={true}
        onClose={vi.fn()}
        projectId={1}
      />
    );

    const titleInput = screen.getByLabelText('タイトル');
    fireEvent.change(titleInput, { target: { value: '' } });

    const saveButton = screen.getByText('保存');
    expect(saveButton).toBeDisabled();
  });

  it('shows correct status options', () => {
    renderWithQueryClient(
      <TaskDetailDialog
        task={mockTask}
        isOpen={true}
        onClose={vi.fn()}
        projectId={1}
      />
    );

    // ステータスセレクターを開く
    const statusSelect = screen.getByLabelText('ステータス').closest('button');
    fireEvent.click(statusSelect);

    expect(screen.getByText('未着手')).toBeInTheDocument();
    expect(screen.getByText('進行中')).toBeInTheDocument();
    expect(screen.getByText('完了')).toBeInTheDocument();
  });

  it('shows correct priority options', () => {
    renderWithQueryClient(
      <TaskDetailDialog
        task={mockTask}
        isOpen={true}
        onClose={vi.fn()}
        projectId={1}
      />
    );

    // 優先度セレクターを開く
    const prioritySelect = screen.getByLabelText('優先度').closest('button');
    fireEvent.click(prioritySelect);

    expect(screen.getByText('低')).toBeInTheDocument();
    expect(screen.getByText('中')).toBeInTheDocument();
    expect(screen.getByText('高')).toBeInTheDocument();
  });

  it('renders date fields correctly', () => {
    const taskWithDates: Task = {
      ...mockTask,
      start_date: '2026-03-24T00:00:00Z',
      end_date: '2026-03-30T00:00:00Z',
    };

    renderWithQueryClient(
      <TaskDetailDialog
        task={taskWithDates}
        isOpen={true}
        onClose={vi.fn()}
        projectId={1}
      />
    );

    const startInput = screen.getByLabelText('開始日');
    const endInput = screen.getByLabelText('終了日');

    expect(startInput).toHaveValue('2026-03-24');
    expect(endInput).toHaveValue('2026-03-30');
  });

  it('renders estimate field correctly', () => {
    renderWithQueryClient(
      <TaskDetailDialog
        task={mockTask}
        isOpen={true}
        onClose={vi.fn()}
        projectId={1}
      />
    );

    const estimateInput = screen.getByLabelText('見積もり (h)');
    expect(estimateInput).toHaveValue('4');
  });

  it('handles new task (no existing task)', () => {
    renderWithQueryClient(
      <TaskDetailDialog
        task={null}
        isOpen={true}
        onClose={vi.fn()}
        projectId={1}
      />
    );

    // 新規タスクの場合はダイアログが表示されない
    expect(screen.queryByText('タスク詳細')).not.toBeInTheDocument();
  });
});
