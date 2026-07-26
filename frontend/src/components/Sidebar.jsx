import React from 'react';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  Layers,
  GitCommit,
  PlayCircle, 
  Cpu, 
  BarChart3, 
  History, 
  Activity, 
  Leaf, 
  ShieldCheck,
  ChevronRight,
  Sparkles,
  Zap
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview Dashboard', icon: LayoutDashboard },
  { id: 'digital-twin', label: 'AI Digital Twin & Heatmap', icon: Layers },
  { id: 'decision-tree', label: 'XAI Live Decision Tree', icon: GitCommit },
  { id: 'simulation', label: 'Simulation Runner', icon: PlayCircle },
  { id: 'optimization', label: 'Multi-Agent Closed Loop', icon: Cpu },
  { id: 'comparison', label: 'Energy Comparison Studio', icon: BarChart3 },
  { id: 'history', label: 'Historical Log & XAI', icon: History },
  { id: 'telemetry', label: 'System Telemetry & Logs', icon: Activity },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <aside className="w-72 bg-[#03060c] border-r border-slate-800/80 flex flex-col justify-between p-4 z-20 select-none shadow-2xl relative">
      {/* Background Subtle Radial Glow */}
      <div className="absolute top-0 left-0 w-full h-48 bg-gradient-to-b from-emerald-500/5 via-cyan-500/5 to-transparent pointer-events-none" />

      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-3 py-4 mb-6 border-b border-slate-800/60 relative">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/25">
              <Leaf className="w-5 h-5 text-slate-950 stroke-[2.5]" />
            </div>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>

          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="text-xl font-extrabold bg-gradient-to-r from-emerald-400 via-teal-200 to-cyan-400 bg-clip-text text-transparent tracking-tight">
                EcoSphere
              </h1>
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <p className="text-[10px] font-bold text-emerald-400/90 tracking-widest uppercase flex items-center gap-1">
              <span>Autonomous Physical AI</span>
            </p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="space-y-1.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`relative w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-xs font-semibold transition-all duration-200 group ${
                  isActive
                    ? 'text-white font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeTabGlow"
                    className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 via-teal-500/15 to-cyan-500/10 rounded-xl border border-emerald-500/40 shadow-lg shadow-emerald-500/10"
                    transition={{ type: 'spring', stiffness: 400, damping: 32 }}
                  />
                )}
                <div className="relative z-10 flex items-center gap-3">
                  <div className={`p-1.5 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                      : 'bg-slate-900/80 text-slate-400 group-hover:text-slate-200 group-hover:bg-slate-800'
                  }`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="tracking-wide">{item.label}</span>
                </div>

                {isActive && (
                  <ChevronRight className="relative z-10 w-4 h-4 text-emerald-400" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer Card */}
      <div className="relative overflow-hidden amoled-card rounded-2xl p-4 border border-emerald-500/25">
        <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl pointer-events-none" />
        
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-bold text-emerald-400 tracking-wide">System Operational</span>
          </div>
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        </div>

        <p className="text-[11px] text-slate-400 font-medium leading-tight">
          FastMCP & EnergyPlus Sandbox Active
        </p>

        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex justify-between items-center text-[10px] text-slate-400 font-mono">
          <span className="flex items-center gap-1">
            <Zap className="w-3 h-3 text-emerald-400" /> v2.4.0
          </span>
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
            READY
          </span>
        </div>
      </div>
    </aside>
  );
}
