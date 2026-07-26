import React from 'react';

export default function StatusBadge({ label, status = 'Online', color = 'emerald' }) {
  const colorStyles = {
    emerald: 'bg-emerald-400 text-emerald-400 border-emerald-500/30 shadow-emerald-500/20',
    cyan: 'bg-cyan-400 text-cyan-400 border-cyan-500/30 shadow-cyan-500/20',
    amber: 'bg-amber-400 text-amber-400 border-amber-500/30 shadow-amber-500/20',
    blue: 'bg-blue-400 text-blue-400 border-blue-500/30 shadow-blue-500/20',
    purple: 'bg-purple-400 text-purple-400 border-purple-500/30 shadow-purple-500/20',
  }[color] || 'bg-emerald-400 text-emerald-400 border-emerald-500/30 shadow-emerald-500/20';

  return (
    <div className="flex items-center justify-between px-3 py-1.5 rounded-xl bg-[#000000] border border-slate-800 text-xs font-mono">
      <span className="text-slate-400 font-semibold">{label}</span>
      <div className="flex items-center gap-1.5">
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${colorStyles.split(' ')[0]}`} />
          <span className={`relative inline-flex rounded-full h-2 w-2 ${colorStyles.split(' ')[0]}`} />
        </span>
        <span className={`font-bold uppercase tracking-wider text-[11px] ${colorStyles.split(' ')[1]}`}>
          {status}
        </span>
      </div>
    </div>
  );
}
