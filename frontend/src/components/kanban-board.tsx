'use client';

import { 
  DndContext, 
  DragOverlay, 
  PointerSensor, 
  useSensor, 
  useSensors,
  closestCorners,
  DragStartEvent,
  DragOverEvent,
  DragEndEvent,
  defaultDropAnimationSideEffects,
} from '@dnd-kit/core';
import { 
  arrayMove, 
  SortableContext, 
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useState, useMemo } from 'react';
import { Task, TaskStatus } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { MoreHorizontal, GripVertical } from 'lucide-react';
import { TaskDetailDialog } from '@/components/task-detail-dialog';
import { useAuthStore } from '@/hooks/use-auth-store';

interface KanbanBoardProps {
  tasks: Task[];
  onTaskUpdate: (taskId: number, newStatus: TaskStatus) => void;
}

const COLUMNS: { id: TaskStatus; title: string }[] = [
  { id: 'todo', title: '未完了' },
  { id: 'doing', title: '進行中' },
  { id: 'done', title: '完了' },
];

export function KanbanBoard({ tasks, onTaskUpdate }: KanbanBoardProps) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    const task = tasks.find((t) => t.id === event.active.id);
    if (task) setActiveTask(task);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    const taskId = active.id as number;
    const overId = over.id as string;

    // もしカラムに移動したなら
    const newStatus = COLUMNS.find(c => c.id === overId)?.id || 
                    tasks.find(t => t.id === Number(overId))?.status;

    if (newStatus && activeTask && activeTask.status !== newStatus) {
      onTaskUpdate(taskId, newStatus as TaskStatus);
    }

    setActiveTask(null);
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full items-start">
        {COLUMNS.map((column) => (
          <KanbanColumn
            key={column.id}
            id={column.id}
            title={column.title}
            tasks={tasks.filter((t) => t.status === column.id)}
            onTaskClick={(task) => {
              setSelectedTask(task);
              setIsDialogOpen(true);
            }}
          />
        ))}
      </div>
      
      <TaskDetailDialog
        task={selectedTask}
        isOpen={isDialogOpen}
        onClose={() => {
          setIsDialogOpen(false);
          setSelectedTask(null);
        }}
        projectId={tasks[0]?.project_id}
      />
      <DragOverlay dropAnimation={{
        sideEffects: defaultDropAnimationSideEffects({
          styles: {
            active: {
              opacity: '0.5',
            },
          },
        }),
      }}>
        {activeTask ? <TaskCard task={activeTask} isDragging /> : null}
      </DragOverlay>
    </DndContext>
  );
}

function KanbanColumn({ id, title, tasks, onTaskClick }: { id: string; title: string; tasks: Task[]; onTaskClick: (task: Task) => void }) {
  return (
    <div className="flex flex-col gap-4 bg-zinc-900/30 p-4 rounded-2xl border border-zinc-800/50 min-h-[500px]">
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-zinc-200">{title}</h3>
          <Badge variant="secondary" className="bg-zinc-800 text-zinc-400 border-none px-1.5 h-5 min-w-5 flex justify-center">
            {tasks.length}
          </Badge>
        </div>
        <button className="text-zinc-600 hover:text-zinc-400 transition-colors">
          <MoreHorizontal className="h-4 w-4" />
        </button>
      </div>

      <SortableContext id={id} items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
        <div className="flex flex-col gap-3">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onClick={() => onTaskClick(task)} />
          ))}
        </div>
      </SortableContext>
    </div>
  );
}

function TaskCard({ task, isDragging, onClick }: { task: Task; isDragging?: boolean; onClick?: () => void }) {
  const {
    setNodeRef,
    attributes,
    listeners,
    transform,
    transition,
  } = useSortable({
    id: task.id,
    data: {
      type: 'Task',
      task,
    },
  });

  const style = {
    transition,
    transform: CSS.Translate.toString(transform),
  };

  const priorityColors = {
    1: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
    2: 'bg-amber-400/10 text-amber-400 border-amber-400/20',
    3: 'bg-rose-400/10 text-rose-400 border-rose-400/20',
  };

  const priorityLabels = {
    1: 'Low',
    2: 'Medium',
    3: 'High',
  };

  return (
    <Card
      ref={setNodeRef}
      style={style}
      className={cn(
        "bg-zinc-900 border-zinc-800 p-4 hover:border-zinc-700 transition-all cursor-default select-none group",
        isDragging && "opacity-50 ring-2 ring-zinc-500 border-zinc-500 shadow-2xl"
      )}
      onClick={onClick}
    >
      <div className="flex flex-col gap-3">
        <div className="flex items-start justify-between">
          <Badge variant="outline" className={cn("text-[10px] uppercase font-bold tracking-wider px-1.5 h-4 border", priorityColors[task.priority])}>
            {priorityLabels[task.priority]}
          </Badge>
          <div {...attributes} {...listeners} className="text-zinc-700 hover:text-zinc-500 cursor-grab active:cursor-grabbing">
            <GripVertical className="h-4 w-4" />
          </div>
        </div>
        
        <h4 className="text-zinc-100 font-medium leading-tight group-hover:text-white transition-colors">
          {task.title}
        </h4>
        
        {task.description && (
          <p className="text-zinc-500 text-xs line-clamp-2">
            {task.description}
          </p>
        )}

        {task.estimate && (
          <div className="flex items-center gap-1.5 mt-1">
            <div className="w-full bg-zinc-800 rounded-full h-1.5">
               <div className="bg-zinc-600 h-1.5 rounded-full" style={{ width: '40%' }} />
            </div>
            <span className="text-[10px] text-zinc-500 font-mono">{task.estimate}h</span>
          </div>
        )}
      </div>
    </Card>
  );
}
