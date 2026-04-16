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
        <h3 className="text-lg font-semibold text-foreground/80">スプリント管理</h3>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="bg-primary text-primary-foreground hover:bg-primary/90 font-semibold rounded-xl" onClick={() => resetForm()}>
              <Plus className="h-4 w-4 mr-2" />
              新規スプリント
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border text-foreground">
            <DialogHeader>
              <DialogTitle className="text-foreground">{editingSprint ? 'スプリント編集' : '新規スプリント作成'}</DialogTitle>
            </DialogHeader>
            <div className="py-4 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="sprint-name" className="text-foreground/70">スプリント名</Label>
                <Input
                  id="sprint-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="bg-background border-border text-foreground focus:ring-primary/20"
                  placeholder="例: Sprint 1"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start-date" className="text-foreground/70">開始日</Label>
                  <Input
                    id="start-date"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="bg-background border-border text-foreground focus:ring-primary/20"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end-date" className="text-foreground/70">終了日</Label>
                  <Input
                    id="end-date"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="bg-background border-border text-foreground focus:ring-primary/20"
                  />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={resetForm}>キャンセル</Button>
              <Button
                onClick={handleSubmit}
                className="bg-primary text-primary-foreground hover:bg-primary/90 font-semibold"
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
          <div className="h-20 bg-secondary/50 rounded-xl animate-pulse" />
        ) : sprints?.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground bg-secondary/30 rounded-xl border border-dashed border-border">
            スプリントがありません
          </div>
        ) : (
          sprints?.map((sprint) => (
            <div
              key={sprint.id}
              className="flex items-center justify-between p-4 bg-card border border-border rounded-xl group hover:border-primary/20 transition-all shadow-sm hover:shadow-md"
            >
              <div className="flex flex-col">
                <span className="font-medium text-foreground/80">{sprint.name}</span>
                <span className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                  <CalendarIcon className="h-3 w-3" />
                  {sprint.start_date ? format(new Date(sprint.start_date), 'MM/dd') : '未設定'} - {sprint.end_date ? format(new Date(sprint.end_date), 'MM/dd') : '未設定'}
                </span>
              </div>
              <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={() => handleEdit(sprint)}>
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
