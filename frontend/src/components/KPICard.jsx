import React from 'react';
import { motion } from 'framer-motion';

export default function KPICard({ title, value, unit, subtitle, icon: Icon, color = 'emerald' }) {
  const colorStyles = {
    emerald: {
      iconBg: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
      border: 'hover:border-emerald-500/30',
      glow: 'shadow-emerald-500/5',
    },
    cyan: {
      iconBg: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400',
      border: 'hover:border-cyan-500/30',
      glow: 'shadow-cyan-500/5',
    },
    rose: {
      iconBg: 'bg-rose-500/10 border-rose-500/20 text-rose-400',
      border: 'hover:border-rose-500/30',
      glow: 'shadow-rose-500/5',
    },
    amber: {
      iconBg: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
      border: 'hover:border-amber-500/30',
      glow: 'shadow-amber-500/5',
    },
  }[color] || colorStyles.emerald;

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.2 }}
      className={`glass-panel rounded-2xl p-5 border border-slate-800/80 transition-all duration-200 ${colorStyles.border} ${colorStyles.glow}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-400 tracking-wide uppercase">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-xl border ${colorStyles.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-1.5 mb-1">
        <span className="text-2xl font-bold text-white tracking-tight font-mono">{value}</span>
        {unit && <span className="text-xs font-medium text-slate-400">{unit}</span>}
      </div>

      {subtitle && <p className="text-[11px] font-medium text-slate-400">{subtitle}</p>}
    </motion.div>
  );
}
