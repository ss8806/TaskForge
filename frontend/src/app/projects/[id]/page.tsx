'use client';

import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi, tasksApi, aiApi, sprintsApi } from '@/lib/api';
import { KanbanBoard } from '@/components/kanban-board';
import { ScrumView } from '@/components/scrum-view';
import { SprintManager } from '@/components/sprint-manager';
import { GanttChartView } from '@/components/gantt-chart-view';
import { TaskDetailDialog } from '@/components/task-detail-dialog';
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
  Calendar,
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
  const [taskForm, setTaskForm] = useState<{title: string, description: string, sprint_id?: number}>({ title: '', description: '', sprint_id: undefined });
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [activeTab, setActiveTab] = useState('kanban');
  const [selectedSprintId, setSelectedSprintId] = useState<string>('all');
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [aiSprintId, setAiSprintId] = useState<string>('none');

  const { data: project, isLoading: isProjectLoading } = useQuery({
    queryKey: ['projects', projectId],
    queryFn: () => projectsApi.get(projectId),
  });

  const { data: tasks, isLoading: isTasksLoading } = useQuery({
    queryKey: ['projects', projectId, 'tasks'],
    queryFn: () => tasksApi.list(projectId),
  });

  const { data: sprints } = useQuery({
    queryKey: ['projects', projectId, 'sprints'],
    queryFn: () => sprintsApi.list(projectId),
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({ taskId, status }: { taskId: number; status: TaskStatus }) =>
      tasksApi.update(taskId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] });
    },
  });

  const createTaskMutation = useMutation({
    mutationFn: (data: any) => tasksApi.create(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] });
      setIsTaskModalOpen(false);
      setTaskForm({ title: '', description: '', sprint_id: undefined });
    },
  });

  const aiDecomposeMutation = useMutation({
    mutationFn: () => aiApi.decompose(projectId, aiPrompt, aiSprintId === 'none' ? undefined : Number(aiSprintId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] });
      setIsAiModalOpen(false);
      setAiPrompt('');
      setAiSprintId('none');
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
                    <div className="space-y-2">
                       <Label>スプリント (任意)</Label>
                       <select 
                         className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100"
                         value={taskForm.sprint_id || ''}
                         onChange={(e) => setTaskForm(prev => ({ ...prev, sprint_id: e.target.value ? Number(e.target.value) : undefined }))}
                       >
                         <option value="">なし (バックログ)</option>
                         {sprints?.map((s: any) => (
                           <option key={s.id} value={s.id}>{s.name}</option>
                         ))}
                       </select>
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

             <Dialog open={isAiModalOpen} onOpenChange={setIsAiModalOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold">
                    <Sparkles className="h-4 w-4 mr-2" />
                    AI分解
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-zinc-900 border-zinc-800 text-zinc-100">
                  <DialogHeader>
                    <DialogTitle>AIタスク分解</DialogTitle>
                    <DialogDescription className="text-zinc-400">
                      やりたいことを入力すると、AIがタスクを自動的に分解して作成します。
                    </DialogDescription>
                  </DialogHeader>
                  <div className="py-4 space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="ai-prompt">要件・アイディア</Label>
                      <Textarea 
                        id="ai-prompt" 
                        placeholder="例: Next.jsでブログサービスを作りたい。ユーザー登録、記事投稿、コメント機能が必要。" 
                        value={aiPrompt}
                        onChange={(e) => setAiPrompt(e.target.value)}
                        className="bg-zinc-800 border-zinc-700 min-h-[120px]" 
                      />
                    </div>
                    <div className="space-y-2">
                       <Label>追加先スプリント (任意)</Label>
                       <select 
                         className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100"
                         value={aiSprintId}
                         onChange={(e) => setAiSprintId(e.target.value)}
                       >
                         <option value="none">なし (バックログ)</option>
                         {sprints?.map((s: any) => (
                           <option key={s.id} value={s.id.toString()}>{s.name}</option>
                         ))}
                       </select>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button 
                      onClick={() => aiDecomposeMutation.mutate()}
                      className="bg-indigo-600 hover:bg-indigo-500 text-white"
                      disabled={aiDecomposeMutation.isPending || !aiPrompt.trim()}
                    >
                      {aiDecomposeMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      AIに任せる
                    </Button>
                  </DialogFooter>
                </DialogContent>
             </Dialog>

             <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm" className="bg-transparent border-zinc-800 text-zinc-400 hover:text-zinc-100 flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    スプリント管理
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-zinc-950 border-zinc-800 text-zinc-100 max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>スプリント管理</DialogTitle>
                    <DialogDescription>
                      プロジェクトのスプリントを管理します。
                    </DialogDescription>
                  </DialogHeader>
                  <div className="py-4">
                    <SprintManager projectId={projectId} />
                  </div>
                </DialogContent>
             </Dialog>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full flex flex-col gap-6">
        <div className="flex items-center justify-between">
           <Tabs value={activeTab} onValueChange={setActiveTab} className="w-auto">
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

           {activeTab === 'kanban' && (
             <div className="flex items-center gap-2">
               <span className="text-xs text-zinc-500">表示:</span>
               <select 
                 value={selectedSprintId}
                 onChange={(e) => setSelectedSprintId(e.target.value)}
                 className="bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 rounded-md px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
               >
                 <option value="all">すべてのタスク</option>
                 <option value="backlog">バックログのみ</option>
                 <optgroup label="スプリント">
                   {sprints?.map((s: any) => (
                     <option key={s.id} value={s.id.toString()}>{s.name}</option>
                   ))}
                 </optgroup>
               </select>
             </div>
           )}
        </div>

        <div className="flex-1 min-h-[600px]">
          {isTasksLoading ? (
            <div className="grid grid-cols-3 gap-6">
              {[1, 2, 3].map(i => <div key={i} className="h-[400px] bg-zinc-900/50 rounded-2xl border border-zinc-800 animate-pulse" />)}
            </div>
          ) : activeTab === 'kanban' ? (
            <KanbanBoard 
              tasks={(tasks || []).filter(t => {
                if (selectedSprintId === 'all') return true;
                if (selectedSprintId === 'backlog') return t.sprint_id === null;
                return t.sprint_id === Number(selectedSprintId);
              })} 
              projectId={projectId}
              sprints={sprints || []}
              onTaskUpdate={(taskId, status) => updateTaskMutation.mutate({ taskId, status })}
              onTaskClick={(task) => {
                setSelectedTask(task);
                setIsDetailOpen(true);
              }}
            />
          ) : activeTab === 'scrum' ? (
            <ScrumView 
              projectId={projectId} 
              onTaskClick={(task) => {
                setSelectedTask(task);
                setIsDetailOpen(true);
              }}
            />
          ) : (
            <GanttChartView projectId={projectId} />
          )}
        </div>
      </main>

      <TaskDetailDialog
        task={selectedTask}
        isOpen={isDetailOpen}
        onClose={() => {
          setIsDetailOpen(false);
          setSelectedTask(null);
        }}
        projectId={projectId}
      />
    </div>
  );
}
