'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sprintsApi } from '@/lib/api';
import { Sprint } from '@/types';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CalendarIcon, Plus, Trash2, Edit2, Loader2 } from 'lucide-react';
import { format } from 'date-fns';

interface SprintManagerProps {
  projectId: number;
}

export function SprintManager({ projectId }: SprintManagerProps) {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [editingSprint, setEditingSprint] = useState<Sprint | null>(null);
  const [name, setName] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data: sprints, isLoading } = useQuery({
    queryKey: ['projects', projectId, 'sprints'],
    queryFn: () => sprintsApi.list(projectId).then((res) => res.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => sprintsApi.create(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'sprints'] });
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => sprintsApi.update(projectId, editingSprint!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'sprints'] });
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (sprintId: number) => sprintsApi.delete(projectId, sprintId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'sprints'] });
    },
  });

  const resetForm = () => {
    setName('');
    setStartDate('');
    setEndDate('');
    setEditingSprint(null);
    setIsOpen(false);
  };

  const handleSubmit = () => {
    const data = {
      name,
      start_date: startDate ? new Date(startDate).toISOString() : undefined,
      end_date: endDate ? new Date(endDate).toISOString() : undefined,
    };
    if (editingSprint) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (sprint: Sprint) => {
    setEditingSprint(sprint);
    setName(sprint.name);
    setStartDate(sprint.start_date ? format(new Date(sprint.start_date), 'yyyy-MM-dd') : '');
    setEndDate(sprint.end_date ? format(new Date(sprint.end_date), 'yyyy-MM-dd') : '');
    setIsOpen(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-zinc-200">スプリント管理</h3>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="bg-zinc-100 text-zinc-950 hover:bg-zinc-200" onClick={() => resetForm()}>
              <Plus className="h-4 w-4 mr-2" />
              新規スプリント
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-zinc-900 border-zinc-800 text-zinc-100">
            <DialogHeader>
              <DialogTitle>{editingSprint ? 'スプリント編集' : '新規スプリント作成'}</DialogTitle>
            </DialogHeader>
            <div className="py-4 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="sprint-name">スプリント名</Label>
                <Input
                  id="sprint-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="bg-zinc-800 border-zinc-700"
                  placeholder="例: Sprint 1"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start-date">開始日</Label>
                  <Input
                    id="start-date"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="bg-zinc-800 border-zinc-700"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end-date">終了日</Label>
                  <Input
                    id="end-date"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="bg-zinc-800 border-zinc-700"
                  />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={resetForm}>キャンセル</Button>
              <Button
                onClick={handleSubmit}
                className="bg-zinc-100 text-zinc-950 hover:bg-zinc-200"
                disabled={!name.trim() || createMutation.isPending || updateMutation.isPending}
              >
                {(createMutation.isPending || updateMutation.isPending) && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {editingSprint ? '更新' : '作成'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {isLoading ? (
          <div className="h-20 bg-zinc-900/50 rounded-xl animate-pulse" />
        ) : sprints?.length === 0 ? (
          <div className="text-center py-8 text-zinc-500 bg-zinc-900/30 rounded-xl border border-dashed border-zinc-800">
            スプリントがありません
          </div>
        ) : (
          sprints?.map((sprint) => (
            <div
              key={sprint.id}
              className="flex items-center justify-between p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl group hover:border-zinc-700 transition-all"
            >
              <div className="flex flex-col">
                <span className="font-medium text-zinc-200">{sprint.name}</span>
                <span className="text-xs text-zinc-500 flex items-center gap-1 mt-1">
                  <CalendarIcon className="h-3 w-3" />
                  {sprint.start_date ? format(new Date(sprint.start_date), 'MM/dd') : '未設定'} - {sprint.end_date ? format(new Date(sprint.end_date), 'MM/dd') : '未設定'}
                </span>
              </div>
              <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-500 hover:text-zinc-200" onClick={() => handleEdit(sprint)}>
                  <Edit2 className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-rose-500/50 hover:text-rose-500 hover:bg-rose-500/10" onClick={() => deleteMutation.mutate(sprint.id)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
