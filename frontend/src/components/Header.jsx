import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Play, Loader2, Cpu, Zap, Activity, ShieldAlert } from 'lucide-react';

const PAGE_TITLES = {
  overview: { title: 'Autonomous Command Center', desc: 'Real-time building physics metrics & multi-agent supervisor consensus' },
  'digital-twin': { title: 'AI Digital Twin & Interactive Heatmap', desc: 'Real-time thermal zone representation, ASHRAE-55 PMV compliance & spatial load distribution' },
  'decision-tree': { title: 'XAI Live Decision Tree', desc: 'Transparent hierarchical decision nodes, specialist reasoning & conflict resolution' },
  simulation: { title: 'EnergyPlus Simulation Engine', desc: 'Execute physics-based building thermal & HVAC simulations' },
  optimization: { title: 'Multi-Agent Closed-Loop Engine', desc: 'Autonomous setpoint tuning & eppy AST model modification' },
  comparison: { title: 'Energy Savings Studio', desc: 'Side-by-side kWh performance & percentage reduction analysis' },
  history: { title: 'Audit Trail & Explainable AI', desc: 'Decision history, multi-agent rationale breakdown & XAI reports' },
  telemetry: { title: 'System Telemetry & Stream Logs', desc: 'Agent execution latency metrics & structured JSON logs' },
};

export default function Header({ activeTab, onRefresh, onExecuteClosedLoop, isExecuting }) {
  const current = PAGE_TITLES[activeTab] || PAGE_TITLES.overview;

  return (
    <header className="h-20 border-b border-slate-800/80 bg-[#03060c]/90 backdrop-blur-xl px-8 flex items-center justify-between sticky top-0 z-30 select-none shadow-xl">
      {/* Title & Description */}
      <div>
        <h2 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <span>{current.title}</span>
        </h2>
        <p className="text-xs text-slate-400 font-medium tracking-wide">{current.desc}</p>
      </div>

      {/* Agents Active Pills & Quick Actions */}
      <div className="flex items-center gap-4">
        {/* Agent Swarm Pills */}
        <div className="hidden lg:flex items-center gap-2 bg-[#080d1a] border border-slate-800 rounded-full px-4 py-1.5 text-xs text-slate-300 shadow-inner">
          <span className="flex items-center gap-1.5 text-emerald-400 font-bold tracking-wide">
            <Cpu className="w-3.5 h-3.5 animate-pulse text-emerald-400" /> Swarm:
          </span>
          <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/25 font-mono text-[10px] font-bold">Energy</span>
          <span className="px-2.5 py-0.5 rounded-full bg-rose-500/10 text-rose-300 border border-rose-500/25 font-mono text-[10px] font-bold">Comfort</span>
          <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/25 font-mono text-[10px] font-bold">Cost</span>
          <span className="px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/25 font-mono text-[10px] font-bold">Sustain</span>
          <span className="px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/25 font-mono text-[10px] font-bold">Supervisor</span>
        </div>

        {/* Refresh Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onRefresh}
          className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition shadow-lg"
          title="Refresh Dashboard Data"
        >
          <RefreshCw className="w-4 h-4 active:animate-spin" />
        </motion.button>

        {/* Execute Closed Loop Button */}
        <motion.button
          whileHover={{ scale: isExecuting ? 1 : 1.03 }}
          whileTap={{ scale: isExecuting ? 1 : 0.96 }}
          onClick={onExecuteClosedLoop}
          disabled={isExecuting}
          className={`relative flex items-center gap-2.5 px-5 py-2.5 rounded-xl font-bold text-xs transition-all shadow-xl overflow-hidden ${
            isExecuting
              ? 'bg-slate-900 text-slate-400 border border-emerald-500/40 cursor-wait'
              : 'bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-slate-950 hover:from-emerald-400 hover:to-cyan-400 shadow-emerald-500/20'
          }`}
        >
          {isExecuting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
              <span className="text-emerald-300 animate-pulse font-mono">Executing AI Swarm Loop...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Execute Closed Loop</span>
            </>
          )}
        </motion.button>
      </div>
    </header>
  );
}
