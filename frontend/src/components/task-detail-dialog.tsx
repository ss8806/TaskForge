'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi, sprintsApi } from '@/lib/api';
import { Task, Sprint, TaskStatus, TaskPriority } from '@/types';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, Trash2, Calendar, Clock, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

interface TaskDetailDialogProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  projectId: number;
}

export function TaskDetailDialog({ task, isOpen, onClose, projectId }: TaskDetailDialogProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'todo' as TaskStatus,
    priority: 2 as TaskPriority,
    start_date: '',
    end_date: '',
    estimate: '',
    sprint_id: 'none' as string | number,
  });

  const { data: sprints } = useQuery({
    queryKey: ['projects', projectId, 'sprints'],
    queryFn: () => sprintsApi.list(projectId).then((res) => res.data),
    enabled: !!projectId,
  });

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title || '',
        description: task.description || '',
        status: task.status,
        priority: task.priority,
        start_date: task.start_date ? format(new Date(task.start_date), 'yyyy-MM-dd') : '',
        end_date: task.end_date ? format(new Date(task.end_date), 'yyyy-MM-dd') : '',
        estimate: task.estimate?.toString() || '',
        sprint_id: task.sprint_id ?? 'none',
      });
    }
  }, [task]);

  const updateMutation = useMutation({
    mutationFn: (data: any) => tasksApi.update(task!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] });
      onClose();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => tasksApi.delete(task!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] });
      onClose();
    },
  });

  const handleSave = () => {
    if (!task) return;
    const data = {
      ...formData,
      estimate: formData.estimate ? parseFloat(formData.estimate) : null,
      sprint_id: formData.sprint_id === 'none' ? null : Number(formData.sprint_id),
      start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
      end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null,
    };
    updateMutation.mutate(data);
  };

  if (!task) return null;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="bg-card border-border text-foreground max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold flex items-center gap-2">
            タスク詳細
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="edit-title">タイトル</Label>
            <Input
              id="edit-title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="bg-background border-border text-foreground focus:ring-primary/20"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-desc">説明</Label>
            <Textarea
              id="edit-desc"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="bg-background border-border text-foreground focus:ring-primary/20 min-h-[100px]"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>ステータス</Label>
              <Select
                value={formData.status}
                onValueChange={(val) => setFormData({ ...formData, status: val as TaskStatus })}
              >
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-border text-foreground">
                  <SelectItem value="todo">未着手</SelectItem>
                  <SelectItem value="doing">進行中</SelectItem>
                  <SelectItem value="done">完了</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>優先度</Label>
              <Select
                value={formData.priority.toString()}
                onValueChange={(val) => setFormData({ ...formData, priority: parseInt(val) as TaskPriority })}
              >
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-border text-foreground">
                  <SelectItem value="1">低 (Low)</SelectItem>
                  <SelectItem value="2">中 (Medium)</SelectItem>
                  <SelectItem value="3">高 (High)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="edit-start">開始日</Label>
              <Input
                id="edit-start"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-end">終了日</Label>
              <Input
                id="edit-end"
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="edit-estimate">見積もり (h)</Label>
              <Input
                id="edit-estimate"
                type="number"
                step="0.5"
                value={formData.estimate}
                onChange={(e) => setFormData({ ...formData, estimate: e.target.value })}
                className="bg-background border-border text-foreground focus:ring-primary/20"
              />
            </div>
            <div className="space-y-2">
              <Label>スプリント</Label>
              <Select
                value={formData.sprint_id?.toString()}
                onValueChange={(val) => setFormData({ ...formData, sprint_id: val === 'none' ? 'none' : parseInt(val) })}
              >
                <SelectTrigger className="bg-background border-border">
                  <SelectValue placeholder="スプリントなし" />
                </SelectTrigger>
                <SelectContent className="bg-card border-border text-foreground">
                  <SelectItem value="none">なし</SelectItem>
                  {sprints?.map((s) => (
                    <SelectItem key={s.id} value={s.id.toString()}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <DialogFooter className="flex justify-between items-center sm:justify-between w-full">
          <Button
            variant="ghost"
            className="text-rose-500 hover:text-rose-400 hover:bg-rose-500/10"
            onClick={() => {
              if (confirm('このタスクを削除しますか？')) {
                deleteMutation.mutate();
              }
            }}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
            <span className="ml-2">削除</span>
          </Button>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>
              キャンセル
            </Button>
            <Button
              className="bg-primary text-primary-foreground hover:bg-primary/90 font-semibold"
              onClick={handleSave}
              disabled={updateMutation.isPending || !formData.title.trim()}
            >
              {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              保存
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
