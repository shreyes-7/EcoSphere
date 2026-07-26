import React from 'react';
import { ExternalLink } from 'lucide-react';

export default function QuickLink({ label, href, onClick, isExternal = false }) {
  if (isExternal) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-xs text-slate-400 hover:text-emerald-400 transition flex items-center gap-1 font-medium group"
      >
        <span className="group-hover:underline">{label}</span>
        <ExternalLink className="w-3 h-3 text-slate-500 group-hover:text-emerald-400 transition" />
      </a>
    );
  }

  return (
    <button
      onClick={onClick}
      className="text-xs text-slate-400 hover:text-emerald-400 transition text-left font-medium hover:underline block"
    >
      {label}
    </button>
  );
}
