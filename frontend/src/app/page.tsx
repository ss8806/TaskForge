'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Sparkles, ArrowRight, Layout, Zap, Brain, Shield } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">
      {/* Background Effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/5 blur-[120px] rounded-full" />
        <div className="absolute bottom-[10%] right-[-5%] w-[30%] h-[30%] bg-primary/5 blur-[100px] rounded-full" />
      </div>

      {/* Nav */}
      <nav className="relative z-10 max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary">
            <Sparkles className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="font-bold text-xl tracking-tight">TaskForge</span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            ログイン
          </Link>
          <Link href="/register">
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90 font-semibold rounded-full px-6">
              無料で始める
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-32">
        <div className="text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary border border-border text-muted-foreground text-xs font-medium translate-y-[-20px] animate-in fade-in slide-in-from-bottom-4 duration-1000">
             <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
             AI-Powered Management
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tighter max-w-4xl mx-auto leading-[1.1] animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
            プロジェクト管理を、<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-primary/80 to-primary/60">
              インテリジェントに加速させる。
            </span>
          </h1>
          
          <p className="max-w-xl mx-auto text-muted-foreground text-lg md:text-xl animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
            TaskForgeは、言語解析AIを搭載した次世代のプロジェクト管理ツールです。要件を入力するだけで、タスク分解からスケジュール提案まで自動化します。
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4 animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-500">
            <Link href="/register">
              <Button size="lg" className="h-14 px-8 bg-primary text-primary-foreground hover:bg-primary/90 text-lg font-bold rounded-2xl shadow-xl shadow-primary/20 group">
                今すぐ始める
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="h-14 px-8 border-border text-foreground hover:bg-secondary text-lg font-bold rounded-2xl">
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
             <div key={i} className="group p-8 rounded-3xl bg-secondary/50 border border-border hover:border-primary/30 transition-all">
                <div className="p-3 rounded-2xl bg-primary/10 border border-primary/20 w-fit mb-6 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.desc}</p>
             </div>
           ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
           <div className="flex items-center gap-2 opacity-50">
             <Sparkles className="h-4 w-4" />
             <span className="font-bold text-sm tracking-tight text-foreground">TaskForge © 2026</span>
           </div>
           <div className="flex gap-8 text-sm text-muted-foreground">
             <a href="#" className="hover:text-primary">Privacy</a>
             <a href="#" className="hover:text-primary">Terms</a>
             <a href="#" className="hover:text-primary">GitHub</a>
           </div>
        </div>
      </footer>
    </div>
  );
}
