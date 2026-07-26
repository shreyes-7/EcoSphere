import React from 'react';

export default function TechnologyBadge({ name, category }) {
  return (
    <div className="px-2.5 py-1 rounded-lg bg-[#000000] border border-slate-800 text-[11px] font-mono text-slate-300 hover:text-white hover:border-emerald-500/50 hover:shadow-sm hover:shadow-emerald-500/10 transition cursor-default flex items-center gap-1.5">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400/80" />
      <span>{name}</span>
      {category && <span className="text-[9px] text-slate-500 font-sans">({category})</span>}
    </div>
  );
}
