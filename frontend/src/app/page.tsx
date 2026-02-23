'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Sparkles, ArrowRight, Layout, Zap, Brain, Shield } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 overflow-hidden">
      {/* Background Effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[10%] right-[-5%] w-[30%] h-[30%] bg-zinc-500/10 blur-[100px] rounded-full" />
      </div>

      {/* Nav */}
      <nav className="relative z-10 max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-zinc-100">
            <Sparkles className="h-5 w-5 text-zinc-950" />
          </div>
          <span className="font-bold text-xl tracking-tight">TaskForge</span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/login" className="text-sm font-medium text-zinc-400 hover:text-zinc-100 transition-colors">
            ログイン
          </Link>
          <Link href="/register">
            <Button className="bg-zinc-100 text-zinc-950 hover:bg-zinc-200 font-semibold rounded-full px-6">
              無料で始める
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-32">
        <div className="text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs font-medium translate-y-[-20px] animate-in fade-in slide-in-from-bottom-4 duration-1000">
             <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
             AI-Powered Management
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tighter max-w-4xl mx-auto leading-[1.1] animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
            プロジェクト管理を、<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-zinc-100 via-zinc-400 to-zinc-600">
              インテリジェントに加速させる。
            </span>
          </h1>
          
          <p className="max-w-xl mx-auto text-zinc-400 text-lg md:text-xl animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
            TaskForgeは、言語解析AIを搭載した次世代のプロジェクト管理ツールです。要件を入力するだけで、タスク分解からスケジュール提案まで自動化します。
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4 animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-500">
            <Link href="/register">
              <Button size="lg" className="h-14 px-8 bg-zinc-100 text-zinc-950 hover:bg-zinc-200 text-lg font-bold rounded-2xl shadow-2xl shadow-white/10 group">
                今すぐ始める
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="h-14 px-8 border-zinc-800 text-zinc-300 hover:text-zinc-100 hover:bg-zinc-900 text-lg font-bold rounded-2xl">
              ドキュメントを読む
            </Button>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32">
           {[
             { icon: Brain, title: "AI自動分解", desc: "自然言語の要件からエピック、タスク、工数見積もりを瞬時に生成。" },
             { icon: Layout, title: "動的ビュー", desc: "カンバン、スクラム、ガントチャートを1クリックでシームレスに切替。" },
             { icon: Shield, title: "エンタープライズ品質", desc: "洗練されたUI/UXと堅牢なセキュリティでチームの生産性を最大化。" }
           ].map((feature, i) => (
             <div key={i} className="group p-8 rounded-3xl bg-zinc-900/40 border border-zinc-900 hover:border-zinc-800 transition-all">
                <div className="p-3 rounded-2xl bg-zinc-900 border border-zinc-800 w-fit mb-6 group-hover:bg-zinc-800 transition-colors">
                  <feature.icon className="h-6 w-6 text-zinc-100" />
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-zinc-500 leading-relaxed">{feature.desc}</p>
             </div>
           ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-900 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
           <div className="flex items-center gap-2 opacity-50">
             <Sparkles className="h-4 w-4" />
             <span className="font-bold text-sm tracking-tight">TaskForge © 2026</span>
           </div>
           <div className="flex gap-8 text-sm text-zinc-600">
             <a href="#" className="hover:text-zinc-400">Privacy</a>
             <a href="#" className="hover:text-zinc-400">Terms</a>
             <a href="#" className="hover:text-zinc-400">GitHub</a>
           </div>
        </div>
      </footer>
    </div>
  );
}
