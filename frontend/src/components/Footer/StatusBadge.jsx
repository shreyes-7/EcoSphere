import React from 'react';

export default function StatusBadge({ label, status = 'Online', color = 'emerald' }) {
  const colorStyles = {
    emerald: 'text-emerald-400',
    cyan: 'text-cyan-400',
    amber: 'text-amber-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
  }[color] || 'text-emerald-400';

  const dotBg = {
    emerald: 'bg-emerald-400',
    cyan: 'bg-cyan-400',
    amber: 'bg-amber-400',
    blue: 'bg-blue-400',
    purple: 'bg-purple-400',
  }[color] || 'bg-emerald-400';

  return (
    <div className="flex items-center justify-between gap-3 px-3 py-1.5 rounded-xl bg-[#000000] border border-slate-800 text-[11px] font-mono w-full">
      <span className="text-slate-300 font-semibold whitespace-nowrap">{label}</span>
      <div className="flex items-center gap-1.5 shrink-0">
        <span className="relative flex h-2 w-2 shrink-0">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotBg}`} />
          <span className={`relative inline-flex rounded-full h-2 w-2 ${dotBg}`} />
        </span>
        <span className={`font-bold uppercase tracking-wider text-[10px] whitespace-nowrap ${colorStyles}`}>
          {status}
        </span>
      </div>
    </div>
  );
}
