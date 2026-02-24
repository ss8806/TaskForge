'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi, sprintsApi } from '@/lib/api';
import { Task, Sprint, TaskStatus } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  ChevronRight, 
  ChevronDown, 
  Layout, 
  ListTodo, 
  Calendar,
  MoreVertical,
  CheckCircle2,
  Circle,
  Clock
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

interface ScrumViewProps {
  projectId: number;
}

export function ScrumView({ projectId }: ScrumViewProps) {
  const queryClient = useQueryClient();
  const [expandedSprints, setExpandedSprints] = useState<Record<number, boolean>>({});

  const { data: sprints, isLoading: isSprintsLoading } = useQuery({
    queryKey: ['projects', projectId, 'sprints'],
    queryFn: () => sprintsApi.list(projectId).then((res) => res.data),
  });

  const { data: tasks, isLoading: isTasksLoading } = useQuery({
    queryKey: ['projects', projectId, 'tasks'],
    queryFn: () => tasksApi.list(projectId).then((res) => res.data),
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({ taskId, data }: { taskId: number; data: any }) =>
      tasksApi.update(taskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] });
    },
  });

  const toggleSprint = (sprintId: number) => {
    setExpandedSprints(prev => ({
      ...prev,
      [sprintId]: !prev[sprintId]
    }));
  };

  if (isSprintsLoading || isTasksLoading) {
    return <div className="space-y-4">
      {[1, 2, 3].map(i => <div key={i} className="h-20 bg-zinc-900/50 rounded-xl animate-pulse" />)}
    </div>;
  }

  const backlogTasks = tasks?.filter(t => t.sprint_id === null) || [];
  
  return (
    <div className="flex flex-col gap-8">
      {/* Sprints Sections */}
      <div className="space-y-4">
        <h3 className="text-zinc-400 text-sm font-medium uppercase tracking-wider px-2">アクティブ & 将来のスプリント</h3>
        {sprints?.length === 0 ? (
          <div className="text-center py-10 bg-zinc-900/30 rounded-2xl border border-dashed border-zinc-800 text-zinc-500">
            スプリントがまだ作成されていません。
          </div>
        ) : (
          sprints?.map(sprint => (
            <SprintSection 
              key={sprint.id} 
              sprint={sprint} 
              tasks={tasks?.filter(t => t.sprint_id === sprint.id) || []}
              isExpanded={expandedSprints[sprint.id] ?? true}
              onToggle={() => toggleSprint(sprint.id)}
              onMoveToBacklog={(taskId) => updateTaskMutation.mutate({ taskId, data: { sprint_id: null } })}
            />
          ))
        )}
      </div>

      {/* Backlog Section */}
      <div className="space-y-4">
        <h3 className="text-zinc-400 text-sm font-medium uppercase tracking-wider px-2">プロダクトバックログ</h3>
        <div className="bg-zinc-900/30 rounded-2xl border border-zinc-800 p-4">
          {backlogTasks.length === 0 ? (
            <div className="text-center py-6 text-zinc-500 text-sm">
              バックログにタスクはありません
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {backlogTasks.map(task => (
                <BacklogTaskCard 
                  key={task.id} 
                  task={task} 
                  sprints={sprints || []}
                  onAssignSprint={(sprintId) => updateTaskMutation.mutate({ taskId: task.id, data: { sprint_id: sprintId } })}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SprintSection({ 
  sprint, 
  tasks, 
  isExpanded, 
  onToggle,
  onMoveToBacklog 
}: { 
  sprint: Sprint; 
  tasks: Task[]; 
  isExpanded: boolean; 
  onToggle: () => void;
  onMoveToBacklog: (taskId: number) => void;
}) {
  const completedTasks = tasks.filter(t => t.status === 'done').length;
  const progress = tasks.length > 0 ? (completedTasks / tasks.length) * 100 : 0;

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl overflow-hidden transition-all hover:border-zinc-700">
      <div 
        className="p-4 flex items-center justify-between cursor-pointer select-none"
        onClick={onToggle}
      >
        <div className="flex items-center gap-4">
          <div className="text-zinc-500">
            {isExpanded ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          </div>
          <div>
            <h4 className="font-bold text-zinc-100">{sprint.name}</h4>
            <p className="text-xs text-zinc-500">
              {sprint.start_date ? format(new Date(sprint.start_date), 'MM/dd') : '?'} - {sprint.end_date ? format(new Date(sprint.end_date), 'MM/dd') : '?'}
              {' · '}{tasks.length} タスク
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end gap-1.5 w-32 hidden sm:flex">
             <div className="flex justify-between w-full text-[10px] text-zinc-500 font-medium">
               <span>進捗</span>
               <span>{Math.round(progress)}%</span>
             </div>
             <div className="w-full bg-zinc-800 rounded-full h-1.5">
               <div 
                 className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500" 
                 style={{ width: `${progress}%` }} 
               />
             </div>
          </div>
          <Button variant="ghost" size="icon" className="text-zinc-500">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-zinc-800/50 p-2">
          {tasks.length === 0 ? (
            <div className="p-8 text-center text-zinc-600 text-sm">
              このスプリントにタスクはありません。バックログから移動してください。
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {tasks.map(task => (
                <div 
                  key={task.id}
                  className="group flex items-center justify-between p-3 rounded-xl hover:bg-zinc-800/50 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <TaskStatusIcon status={task.status} />
                    <span className={cn("text-sm text-zinc-300 truncate", task.status === 'done' && "line-through text-zinc-600")}>
                      {task.title}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 shrink-0 px-2">
                    {task.estimate && <span className="text-[10px] text-zinc-500 font-mono">{task.estimate}h</span>}
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-7 text-[10px] text-zinc-500 hover:text-zinc-300 opacity-0 group-hover:opacity-100"
                      onClick={(e) => {
                        e.stopPropagation();
                        onMoveToBacklog(task.id);
                      }}
                    >
                      バックログへ
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function BacklogTaskCard({ 
  task, 
  sprints, 
  onAssignSprint 
}: { 
  task: Task; 
  sprints: Sprint[]; 
  onAssignSprint: (sprintId: number) => void;
}) {
  const priorityColors = {
    1: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    2: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    3: 'text-rose-400 bg-rose-400/10 border-rose-400/20',
  };

  return (
    <div className="group flex items-center justify-between p-3 rounded-xl bg-zinc-900/50 border border-zinc-800/50 hover:border-zinc-700 transition-all">
      <div className="flex items-center gap-3 min-w-0">
        <Badge variant="outline" className={cn("text-[8px] h-4 px-1", priorityColors[task.priority])}>
          {task.priority === 3 ? 'High' : task.priority === 2 ? 'Med' : 'Low'}
        </Badge>
        <span className="text-sm text-zinc-300 font-medium truncate">{task.title}</span>
      </div>
      <div className="flex items-center gap-2">
        {sprints.map(sprint => (
          <Button
            key={sprint.id}
            variant="outline"
            size="sm"
            className="h-7 px-2 text-[10px] border-zinc-800 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 opacity-0 group-hover:opacity-100 transition-all"
            onClick={() => onAssignSprint(sprint.id)}
          >
            {sprint.name}
          </Button>
        ))}
      </div>
    </div>
  );
}

function TaskStatusIcon({ status }: { status: TaskStatus }) {
  switch (status) {
    case 'done': return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
    case 'doing': return <Clock className="h-4 w-4 text-amber-500" />;
    default: return <Circle className="h-4 w-4 text-zinc-600" />;
  }
}
