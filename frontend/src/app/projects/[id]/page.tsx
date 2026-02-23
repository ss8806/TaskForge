'use client';

import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi, tasksApi } from '@/lib/api';
import { KanbanBoard } from '@/components/kanban-board';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Plus, 
  ArrowLeft, 
  Settings, 
  Layout, 
  ListTodo, 
  BarChart3, 
  Sparkles,
  Loader2
} from 'lucide-react';
import { useState } from 'react';
import { TaskStatus } from '@/types';

export default function ProjectPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const projectId = Number(params.id);

  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [taskForm, setTaskForm] = useState({ title: '', description: '' });

  const { data: project, isLoading: isProjectLoading } = useQuery({
    queryKey: ['projects', projectId],
    queryFn: () => projectsApi.get(projectId).then((res) => res.data),
  });

  const { data: tasks, isLoading: isTasksLoading } = useQuery({
    queryKey: ['projects', projectId, 'tasks'],
    queryFn: () => tasksApi.list(projectId).then((res) => res.data),
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({ taskId, status }: { taskId: number; status: TaskStatus }) =>
      tasksApi.update(taskId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] });
    },
  });

  const createTaskMutation = useMutation({
    mutationFn: (data: typeof taskForm) => tasksApi.create(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] });
      setIsTaskModalOpen(false);
      setTaskForm({ title: '', description: '' });
    },
  });

  if (isProjectLoading) return <div className="flex items-center justify-center min-h-screen bg-zinc-950 text-white"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/dashboard')} className="text-zinc-500 hover:text-zinc-100">
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2">
              <div className="p-1 rounded bg-zinc-800">
                <Layout className="h-4 w-4 text-zinc-400" />
              </div>
              <h1 className="font-bold text-lg tracking-tight">{project?.name}</h1>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
             <Button variant="outline" size="sm" className="bg-transparent border-zinc-800 text-zinc-400 hover:text-zinc-100 hidden sm:flex">
               <Settings className="h-4 w-4 mr-2" />
               設定
             </Button>
             <Dialog open={isTaskModalOpen} onOpenChange={setIsTaskModalOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" className="bg-zinc-100 text-zinc-950 hover:bg-zinc-200 font-semibold">
                    <Plus className="h-4 w-4 mr-2" />
                    タスク追加
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-zinc-900 border-zinc-800 text-zinc-100">
                  <DialogHeader>
                    <DialogTitle>新規タスク</DialogTitle>
                  </DialogHeader>
                  <div className="py-4 space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="title">タイトル</Label>
                      <Input 
                        id="title" 
                        value={taskForm.title}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, title: e.target.value }))}
                        className="bg-zinc-800 border-zinc-700" 
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="desc">説明</Label>
                      <Textarea 
                        id="desc" 
                        value={taskForm.description}
                        onChange={(e) => setTaskForm(prev => ({ ...prev, description: e.target.value }))}
                        className="bg-zinc-800 border-zinc-700 min-h-[100px]" 
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button 
                      onClick={() => createTaskMutation.mutate(taskForm)}
                      className="bg-zinc-100 text-zinc-950"
                      disabled={!taskForm.title}
                    >
                      {createTaskMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      追加
                    </Button>
                  </DialogFooter>
                </DialogContent>
             </Dialog>

             <Button size="sm" className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold">
               <Sparkles className="h-4 w-4 mr-2" />
               AI分解
             </Button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full flex flex-col gap-6">
        <div className="flex items-center justify-between">
           <Tabs defaultValue="kanban" className="w-auto">
             <TabsList className="bg-zinc-900 border border-zinc-800 h-10 p-1">
               <TabsTrigger value="kanban" className="data-[state=active]:bg-zinc-800 data-[state=active]:text-zinc-100 h-8 flex gap-2">
                 <Layout className="h-3.5 w-3.5" />
                 カンバン
               </TabsTrigger>
               <TabsTrigger value="scrum" className="data-[state=active]:bg-zinc-800 data-[state=active]:text-zinc-100 h-8 flex gap-2">
                 <ListTodo className="h-3.5 w-3.5" />
                 スクラム
               </TabsTrigger>
               <TabsTrigger value="gantt" className="data-[state=active]:bg-zinc-800 data-[state=active]:text-zinc-100 h-8 flex gap-2">
                 <BarChart3 className="h-3.5 w-3.5" />
                 ガント
               </TabsTrigger>
             </TabsList>
           </Tabs>
        </div>

        <div className="flex-1 min-h-[600px]">
          {isTasksLoading ? (
            <div className="grid grid-cols-3 gap-6">
              {[1, 2, 3].map(i => <div key={i} className="h-[400px] bg-zinc-900/50 rounded-2xl border border-zinc-800 animate-pulse" />)}
            </div>
          ) : (
            <KanbanBoard 
              tasks={tasks || []} 
              onTaskUpdate={(taskId, status) => updateTaskMutation.mutate({ taskId, status })} 
            />
          )}
        </div>
      </main>
    </div>
  );
}
