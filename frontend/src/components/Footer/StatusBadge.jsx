import React from 'react';

export default function StatusBadge({ label, status = 'Online', color = 'emerald' }) {
  const colorStyles = {
    emerald: 'bg-emerald-400 text-emerald-400 border-emerald-500/30',
    cyan: 'bg-cyan-400 text-cyan-400 border-cyan-500/30',
    amber: 'bg-amber-400 text-amber-400 border-amber-500/30',
    blue: 'bg-blue-400 text-blue-400 border-blue-500/30',
    purple: 'bg-purple-400 text-purple-400 border-purple-500/30',
  }[color] || 'bg-emerald-400 text-emerald-400 border-emerald-500/30';

  const dotBg = colorStyles.split(' ')[0];
  const textColor = colorStyles.split(' ')[1];

  return (
    <div className="flex items-center justify-between gap-2 px-2.5 py-1.5 rounded-xl bg-[#000000] border border-slate-800 text-[11px] font-mono min-w-0">
      <span className="text-slate-400 font-semibold truncate">{label}</span>
      <div className="flex items-center gap-1.5 shrink-0">
        <span className="relative flex h-2 w-2 shrink-0">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotBg}`} />
          <span className={`relative inline-flex rounded-full h-2 w-2 ${dotBg}`} />
        </span>
        <span className={`font-bold uppercase tracking-wider text-[10px] ${textColor}`}>
          {status}
        </span>
      </div>
    </div>
  );
}
