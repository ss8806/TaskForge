'use client';

import { useQuery } from '@tanstack/react-query';
import { tasksApi } from '@/lib/api';
import { Task } from '@/types';
import { 
  format, 
  addDays, 
  startOfToday, 
  isSameDay, 
  eachDayOfInterval, 
  differenceInDays, 
  startOfMonth,
  endOfMonth,
  isWithinInterval,
  parseISO
} from 'date-fns';
import { ja } from 'date-fns/locale';
import { useState, useMemo, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface GanttChartViewProps {
  projectId: number;
}

const COLUMN_WIDTH = 40; // width of each day column in pixels

export function GanttChartView({ projectId }: GanttChartViewProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [viewDate, setViewDate] = useState(startOfToday());
  
  // Display a 3-week window starting from 3 days before viewDate
  const startDate = useMemo(() => addDays(viewDate, -3), [viewDate]);
  const endDate = useMemo(() => addDays(startDate, 21), [startDate]);
  
  const days = useMemo(() => {
    return eachDayOfInterval({ start: startDate, end: endDate });
  }, [startDate, endDate]);

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['projects', projectId, 'tasks'],
    queryFn: () => tasksApi.list(projectId).then((res) => res.data),
  });

  // Scroll to "today" on initial load
  useEffect(() => {
    if (scrollContainerRef.current) {
      const today = startOfToday();
      const diff = differenceInDays(today, startDate);
      if (diff >= 0 && diff < days.length) {
        scrollContainerRef.current.scrollLeft = diff * COLUMN_WIDTH - 100;
      }
    }
  }, [days, startDate]);

  if (isLoading) {
    return <div className="h-[400px] bg-zinc-900/50 rounded-2xl border border-zinc-800 animate-pulse" />;
  }

  return (
    <div className="flex flex-col gap-4 bg-zinc-900/30 rounded-3xl border border-zinc-800 overflow-hidden">
      {/* Gantt Header/Controls */}
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/50">
        <div className="flex items-center gap-4">
          <h3 className="font-bold text-zinc-100 flex items-center gap-2">
            <Calendar className="h-4 w-4 text-indigo-400" />
            タイムライン
          </h3>
          <div className="flex items-center gap-1 bg-zinc-800 rounded-lg p-1">
             <Button variant="ghost" size="icon" className="h-7 w-7 text-zinc-400" onClick={() => setViewDate(d => addDays(d, -7))}>
               <ChevronLeft className="h-4 w-4" />
             </Button>
             <span className="text-xs font-medium px-2 text-zinc-300">
               {format(viewDate, 'yyyy年 MM月', { locale: ja })}
             </span>
             <Button variant="ghost" size="icon" className="h-7 w-7 text-zinc-400" onClick={() => setViewDate(d => addDays(d, 7))}>
               <ChevronRight className="h-4 w-4" />
             </Button>
          </div>
        </div>
        <Button variant="outline" size="sm" className="h-8 border-zinc-700 text-xs" onClick={() => setViewDate(startOfToday())}>
          今日
        </Button>
      </div>

      <div className="flex overflow-hidden h-[500px]">
        {/* Task Names Column */}
        <div className="w-48 shrink-0 border-r border-zinc-800 bg-zinc-950/20 z-10 shadow-xl">
          <div className="h-12 border-b border-zinc-800 flex items-center px-4 bg-zinc-900/50">
             <span className="text-[10px] uppercase font-bold tracking-widest text-zinc-500">タスク名</span>
          </div>
          <div className="overflow-hidden">
            {tasks?.map(task => (
              <div key={task.id} className="h-10 border-b border-zinc-800/50 flex items-center px-4 hover:bg-zinc-800/30 transition-colors">
                <span className="text-xs text-zinc-400 truncate">{task.title}</span>
              </div>
            ))}
            {tasks?.length === 0 && <div className="p-4 text-xs text-zinc-600">タスクなし</div>}
          </div>
        </div>

        {/* Timeline Grid */}
        <div 
          ref={scrollContainerRef}
          className="flex-1 overflow-x-auto overflow-y-hidden scrollbar-hide"
        >
          <div style={{ width: days.length * COLUMN_WIDTH }}>
            {/* Days Header */}
            <div className="h-12 border-b border-zinc-800 flex bg-zinc-900/50">
              {days.map(day => (
                <div 
                  key={day.toISOString()} 
                  className={cn(
                    "shrink-0 border-r border-zinc-800/30 flex flex-col items-center justify-center gap-0.5",
                    isSameDay(day, startOfToday()) && "bg-indigo-500/5"
                  )}
                  style={{ width: COLUMN_WIDTH }}
                >
                  <span className="text-[9px] text-zinc-600 font-medium">
                    {format(day, 'E', { locale: ja })}
                  </span>
                  <span className={cn(
                    "text-[10px] font-bold",
                    isSameDay(day, startOfToday()) ? "text-indigo-400" : "text-zinc-400"
                  )}>
                    {format(day, 'd')}
                  </span>
                </div>
              ))}
            </div>

            {/* Task Rows */}
            <div className="relative">
              {/* Background Grid Lines */}
              <div className="absolute inset-0 flex pointer-events-none">
                {days.map(day => (
                   <div 
                     key={day.toISOString()} 
                     className={cn(
                       "h-full border-r border-zinc-800/20",
                       isSameDay(day, startOfToday()) && "bg-indigo-500/5"
                     )} 
                     style={{ width: COLUMN_WIDTH }} 
                   />
                ))}
              </div>

              {/* Task Bars */}
              <div className="relative z-10">
                {tasks?.map(task => (
                  <div key={task.id} className="h-10 border-b border-zinc-800/30 flex items-center relative">
                    <TaskBar task={task} gridStartDate={startDate} daysCount={days.length} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="p-3 bg-zinc-950/40 border-t border-zinc-800 flex justify-center gap-6 text-[10px] text-zinc-500 italic">
         <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-indigo-500/80" /> 予定あり</div>
         <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-zinc-800" /> 未設定</div>
      </div>
    </div>
  );
}

function TaskBar({ task, gridStartDate, daysCount }: { task: Task, gridStartDate: Date, daysCount: number }) {
  const start = task.start_date ? parseISO(task.start_date) : null;
  const end = task.end_date ? parseISO(task.end_date) : null;

  if (!start) {
    return (
      <div 
        className="absolute h-1.5 bg-zinc-800 rounded-full left-4 opacity-50" 
        style={{ width: COLUMN_WIDTH * 0.8 }} 
        title="日付未設定"
      />
    );
  }

  const effectiveEnd = end || addDays(start, 1);
  const startOffset = differenceInDays(start, gridStartDate);
  const duration = Math.max(1, differenceInDays(effectiveEnd, start) + 1);

  // Don't render if outside the visible interval
  if (startOffset + duration < 0 || startOffset > daysCount) return null;

  const left = Math.max(0, startOffset * COLUMN_WIDTH);
  const width = Math.min(daysCount * COLUMN_WIDTH, duration * COLUMN_WIDTH);

  return (
    <div 
      className={cn(
        "absolute h-6 rounded-lg flex items-center px-2 shadow-lg transition-all hover:scale-[1.02] hover:shadow-indigo-500/20",
        task.status === 'done' ? "bg-zinc-700/50 opacity-40" : "bg-gradient-to-r from-indigo-600 to-indigo-500 border border-white/10"
      )}
      style={{ left, width }}
    >
      <span className="text-[9px] font-bold text-white truncate drop-shadow-sm">
        {task.title}
      </span>
    </div>
  );
}
