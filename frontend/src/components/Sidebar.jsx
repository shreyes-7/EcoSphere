import React from 'react';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  PlayCircle, 
  Cpu, 
  BarChart3, 
  History, 
  Activity, 
  Leaf, 
  ShieldCheck,
  ChevronRight
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview Dashboard', icon: LayoutDashboard },
  { id: 'simulation', label: 'Simulation Runner', icon: PlayCircle },
  { id: 'optimization', label: 'Multi-Agent Closed Loop', icon: Cpu },
  { id: 'comparison', label: 'Energy Comparison Studio', icon: BarChart3 },
  { id: 'history', label: 'Historical Log & XAI', icon: History },
  { id: 'telemetry', label: 'System Telemetry & Logs', icon: Activity },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <aside className="w-72 bg-[#0d1322] border-r border-slate-800/80 flex flex-col justify-between p-4 z-20 select-none">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-3 py-4 mb-6 border-b border-slate-800/60">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Leaf className="w-6 h-6 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent tracking-tight">
              EcoSphere
            </h1>
            <p className="text-[11px] font-medium text-slate-400 tracking-wider uppercase">
              Autonomous Physical AI
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
                className={`relative w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'text-white font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeTabGlow"
                    className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-cyan-500/10 rounded-xl border border-emerald-500/40 shadow-sm"
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
                <div className="relative z-10 flex items-center gap-3">
                  <Icon className={`w-5 h-5 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
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
      <div className="glass-card rounded-2xl p-3.5 border border-emerald-500/20 bg-slate-900/80">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-semibold text-emerald-400">System Online</span>
          </div>
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        </div>
        <p className="text-xs text-slate-400">FastMCP & EnergyPlus Sandbox Active</p>
        <div className="mt-2.5 pt-2 border-t border-slate-800 flex justify-between items-center text-[10px] text-slate-400 font-mono">
          <span>Version 2.4.0</span>
          <span className="text-cyan-400 font-semibold">Ready</span>
        </div>
      </div>
    </aside>
  );
}
