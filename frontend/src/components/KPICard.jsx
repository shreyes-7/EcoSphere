import React from 'react';
import { motion } from 'framer-motion';

export default function KPICard({ title, value, unit, subtitle, icon: Icon, color = 'emerald', trend }) {
  const colorStyles = {
    emerald: {
      iconBg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
      border: 'hover:border-emerald-500/40',
      glow: 'hover:shadow-emerald-500/10',
      pill: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
      gradient: 'from-emerald-500/10 via-transparent to-transparent',
    },
    cyan: {
      iconBg: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400',
      border: 'hover:border-cyan-500/40',
      glow: 'hover:shadow-cyan-500/10',
      pill: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/20',
      gradient: 'from-cyan-500/10 via-transparent to-transparent',
    },
    rose: {
      iconBg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
      border: 'hover:border-rose-500/40',
      glow: 'hover:shadow-rose-500/10',
      pill: 'bg-rose-500/10 text-rose-300 border-rose-500/20',
      gradient: 'from-rose-500/10 via-transparent to-transparent',
    },
    amber: {
      iconBg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
      border: 'hover:border-amber-500/40',
      glow: 'hover:shadow-amber-500/10',
      pill: 'bg-amber-500/10 text-amber-300 border-amber-500/20',
      gradient: 'from-amber-500/10 via-transparent to-transparent',
    },
    purple: {
      iconBg: 'bg-purple-500/10 border-purple-500/30 text-purple-400',
      border: 'hover:border-purple-500/40',
      glow: 'hover:shadow-purple-500/10',
      pill: 'bg-purple-500/10 text-purple-300 border-purple-500/20',
      gradient: 'from-purple-500/10 via-transparent to-transparent',
    },
  }[color] || colorStyles.emerald;

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.2 }}
      className={`relative overflow-hidden amoled-card rounded-2xl p-5 border border-slate-800/90 transition-all duration-300 ${colorStyles.border} ${colorStyles.glow}`}
    >
      {/* Top Subtle Gradient Accents */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${colorStyles.gradient}`} />

      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-bold text-slate-400 tracking-wider uppercase">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-xl border ${colorStyles.iconBg} shadow-inner`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2 mb-1.5">
        <span className="text-3xl font-extrabold text-white tracking-tight font-mono">{value}</span>
        {unit && <span className="text-xs font-semibold text-slate-400">{unit}</span>}

        {trend && (
          <span className={`ml-auto text-[11px] font-mono font-bold px-2 py-0.5 rounded-full border ${colorStyles.pill}`}>
            {trend}
          </span>
        )}
      </div>

      {subtitle && <p className="text-[11px] font-medium text-slate-400/90 tracking-wide">{subtitle}</p>}
    </motion.div>
  );
}
