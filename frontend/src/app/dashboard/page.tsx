'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
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
import { useAuthStore } from '@/hooks/use-auth-store';
import { 
  Plus, 
  LayoutDashboard, 
  LogOut, 
  FolderKanban, 
  Calendar, 
  ChevronRight,
  Sparkles,
  Loader2
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const logout = useAuthStore((state) => state.logout);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  });

  const createMutation = useMutation({
    mutationFn: (name: string) => projectsApi.create({ name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setIsCreateModalOpen(false);
      setNewProjectName('');
    },
  });

  const handleCreateProject = () => {
    if (newProjectName.trim()) {
      createMutation.mutate(newProjectName);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-zinc-100">
              <Sparkles className="h-5 w-5 text-zinc-950" />
            </div>
            <span className="font-bold text-xl tracking-tight">TaskForge</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={logout} className="text-zinc-400 hover:text-zinc-100">
              <LogOut className="h-4 w-4 mr-2" />
              ログアウト
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">プロジェクト</h1>
            <p className="text-zinc-400 mt-1">管理しているプロジェクトの一覧です</p>
          </div>
          <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
            <DialogTrigger asChild>
              <Button className="bg-zinc-100 text-zinc-950 hover:bg-zinc-200 shadow-lg shadow-zinc-100/10 transition-all font-semibold">
                <Plus className="h-4 w-4 mr-2" />
                新規プロジェクト
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-zinc-900 border-zinc-800 text-zinc-100">
              <DialogHeader>
                <DialogTitle>新規プロジェクト作成</DialogTitle>
                <DialogDescription className="text-zinc-400">
                  プロジェクト名を入力して開始しましょう。
                </DialogDescription>
              </DialogHeader>
              <div className="py-4 space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">プロジェクト名</Label>
                  <Input 
                    id="name" 
                    placeholder="例: 次世代アプリ開発" 
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-zinc-100 focus:ring-zinc-600"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="ghost" onClick={() => setIsCreateModalOpen(false)}>キャンセル</Button>
                <Button 
                  onClick={handleCreateProject}
                  className="bg-zinc-100 text-zinc-950 hover:bg-zinc-200"
                  disabled={createMutation.isPending || !newProjectName.trim()}
                >
                  {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  作成する
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 rounded-2xl bg-zinc-900/50 border border-zinc-800 animate-pulse" />
            ))}
          </div>
        ) : projects?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 bg-zinc-900/40 rounded-3xl border border-zinc-800 border-dashed">
            <FolderKanban className="h-12 w-12 text-zinc-700 mb-4" />
            <p className="text-zinc-400 text-lg">プロジェクトがまだありません</p>
            <Button variant="link" className="text-zinc-300" onClick={() => setIsCreateModalOpen(true)}>
              最初のプロジェクトを作成する
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects?.map((project) => (
              <Card 
                key={project.id} 
                className="group cursor-pointer bg-zinc-900/50 border-zinc-800 hover:border-zinc-700 transition-all hover:translate-y-[-2px] overflow-hidden"
                onClick={() => router.push(`/projects/${project.id}`)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl group-hover:text-zinc-100 transition-colors">
                      {project.name}
                    </CardTitle>
                    <ChevronRight className="h-5 w-5 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
                  </div>
                  <CardDescription className="text-zinc-500 line-clamp-2 mt-2">
                    {project.description || '説明なし'}
                  </CardDescription>
                </CardHeader>
                <CardFooter className="pt-4 flex items-center gap-4 text-xs text-zinc-500">
                   <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(project.created_at).toLocaleDateString('ja-JP')}
                   </div>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
