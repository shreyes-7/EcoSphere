import React from 'react';
import { Leaf, Sparkles, Activity, Code2, Link2 } from 'lucide-react';
import StatusBadge from './Footer/StatusBadge';
import TechnologyBadge from './Footer/TechnologyBadge';
import QuickLink from './Footer/QuickLink';

export default function Footer({ onNavigate }) {
  const techStack = [
    'EnergyPlus',
    'FastAPI',
    'React',
    'JavaScript',
    'Python',
    'FastMCP',
    'SQLAlchemy',
    'SQLite',
    'TailwindCSS'
  ];

  return (
    <footer className="w-full max-w-7xl mx-auto mt-12 mb-6 z-10 select-none">
      <div className="amoled-card rounded-3xl p-6 sm:p-8 border border-slate-800/80 space-y-6 shadow-2xl">
        
        {/* Main Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          
          {/* SECTION 1: EcoSphere Platform Info */}
          <div className="space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-500 flex items-center justify-center text-slate-950 shadow-md shadow-emerald-500/20">
                <Leaf className="w-4.5 h-4.5 stroke-[2.5]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-extrabold text-white tracking-tight">EcoSphere</h3>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-mono font-bold">
                    v1.0.0
                  </span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase tracking-wider block">
                  Autonomous Physical AI Platform
                </span>
              </div>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              Real-time Multi-Agent Building Intelligence powered by EnergyPlus physics simulation and explainable AI.
            </p>
          </div>

          {/* SECTION 2: System Health */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>System Health</span>
            </h4>
            <div className="space-y-1.5 w-full">
              <StatusBadge label="API" status="Online" color="emerald" />
              <StatusBadge label="Database" status="Healthy" color="emerald" />
              <StatusBadge label="EnergyPlus" status="Connected" color="cyan" />
              <StatusBadge label="Supervisor" status="Active" color="amber" />
              <StatusBadge label="RL Engine" status="Learning" color="purple" />
              <StatusBadge label="Swarm" status="Running" color="emerald" />
            </div>
          </div>

          {/* SECTION 3: Technology Stack */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Code2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>Technology Stack</span>
            </h4>
            <div className="grid grid-cols-2 gap-1.5">
              {techStack.map((tech) => (
                <TechnologyBadge key={tech} name={tech} />
              ))}
            </div>
          </div>

          {/* SECTION 4: Quick Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Link2 className="w-3.5 h-3.5 text-amber-400" />
              <span>Quick Links</span>
            </h4>
            <div className="space-y-2">
              <QuickLink
                label="About EcoSphere"
                onClick={() => onNavigate && onNavigate('about')}
              />
              <QuickLink
                label="API Documentation"
                isExternal
                href="/docs"
              />
              <QuickLink
                label="Project GitHub Repository"
                isExternal
                href="https://github.com/shreyes-7/EcoSphere"
              />
              <QuickLink
                label="MIT Open Source License"
                onClick={() => onNavigate && onNavigate('about')}
              />
              <QuickLink
                label="System Telemetry Logs"
                onClick={() => onNavigate && onNavigate('telemetry')}
              />
            </div>
          </div>

        </div>

        {/* COPYRIGHT BOTTOM ROW */}
        <div className="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono text-slate-500">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">© 2026 EcoSphere</span>
            <span>•</span>
            <span>Developed for Autonomous Building Intelligence</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
            <span>EnergyPlus & Multi-Agent Physical AI Engine</span>
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
          </div>
        </div>

      </div>
    </footer>
  );
}
