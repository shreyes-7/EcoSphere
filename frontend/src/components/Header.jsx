import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Play, Loader2, Cpu } from 'lucide-react';

const PAGE_TITLES = {
  overview: { title: 'Overview Dashboard', desc: 'Real-time building metrics & supervisor consensus plan' },
  simulation: { title: 'EnergyPlus Simulation Runner', desc: 'Execute physics-based building energy simulations' },
  optimization: { title: 'Multi-Agent Closed-Loop Engine', desc: 'Autonomous setpoint tuning & eppy AST model modification' },
  comparison: { title: 'Energy Comparison Studio', desc: 'Side-by-side kWh performance & savings delta analysis' },
  history: { title: 'Historical Log & Explainable AI Reports', desc: 'Audit trail, decision trees & downloadable CSV/JSON reports' },
  telemetry: { title: 'System Telemetry & Agent Logs', desc: 'Microsecond agent execution latency & structured JSON logs' },
};

export default function Header({ activeTab, onRefresh, onExecuteClosedLoop, isExecuting }) {
  const current = PAGE_TITLES[activeTab] || PAGE_TITLES.overview;

  return (
    <header className="h-20 border-b border-slate-800/80 bg-[#0b0f19]/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-10 select-none">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">{current.title}</h2>
        <p className="text-xs text-slate-400 font-medium">{current.desc}</p>
      </div>

      {/* Agents Active Pills & Quick Actions */}
      <div className="flex items-center gap-4">
        {/* Agent Pills */}
        <div className="hidden lg:flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-full px-3.5 py-1.5 text-xs text-slate-300 shadow-inner">
          <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <Cpu className="w-3.5 h-3.5 animate-pulse text-emerald-400" /> 5 Active Agents:
          </span>
          <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono text-[11px]">Energy</span>
          <span className="px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/20 font-mono text-[11px]">Comfort</span>
          <span className="px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-mono text-[11px]">Cost</span>
          <span className="px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/20 font-mono text-[11px]">Sustain</span>
          <span className="px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-300 border border-purple-500/20 font-mono text-[11px]">Supervisor</span>
        </div>

        {/* Refresh Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onRefresh}
          className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition shadow"
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
          className={`relative flex items-center gap-2.5 px-5 py-2.5 rounded-xl font-bold text-xs transition-all shadow-lg overflow-hidden ${
            isExecuting
              ? 'bg-slate-800 text-slate-400 border border-emerald-500/40 cursor-wait'
              : 'bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-slate-950 hover:from-emerald-400 hover:to-cyan-400 shadow-emerald-500/25'
          }`}
        >
          {isExecuting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
              <span className="text-emerald-300 animate-pulse font-mono">Executing AI Closed Loop...</span>
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
