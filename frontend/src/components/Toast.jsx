import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, AlertCircle, Info, Loader2, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  if (!toast) return null;

  const iconMap = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />,
    error: <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />,
    loading: <Loader2 className="w-5 h-5 text-cyan-400 animate-spin shrink-0" />,
    info: <Info className="w-5 h-5 text-cyan-400 shrink-0" />,
  };

  const borderMap = {
    success: 'border-emerald-500/40 bg-emerald-950/80 text-emerald-100 shadow-emerald-500/10',
    error: 'border-rose-500/40 bg-rose-950/80 text-rose-100 shadow-rose-500/10',
    loading: 'border-cyan-500/40 bg-slate-900/90 text-cyan-100 shadow-cyan-500/10',
    info: 'border-cyan-500/40 bg-slate-900/90 text-cyan-100 shadow-cyan-500/10',
  };

  return (
    <div className="fixed bottom-24 right-6 z-50 pointer-events-none">
      <AnimatePresence>
        <motion.div
          key={toast.id || 'toast'}
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.9 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-2xl border backdrop-blur-lg shadow-xl max-w-md ${borderMap[toast.type] || borderMap.info}`}
        >
          {iconMap[toast.type] || iconMap.info}
          <div className="flex-1 text-xs">
            <span className="font-bold block text-white">{toast.title}</span>
            {toast.message && <p className="text-slate-300 text-[11px] mt-0.5">{toast.message}</p>}
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white transition"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
