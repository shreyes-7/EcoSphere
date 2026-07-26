import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Thermometer, Droplets, Activity, Zap, Cpu, ShieldCheck, UserCheck, AlertTriangle } from 'lucide-react';

export default function ZoneDetailDrawer({ zone, onClose }) {
  if (!zone) return null;

  const colorBadges = {
    green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    orange: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
    red: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    blue: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
    gray: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
  }[zone.color_code] || 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="w-full max-w-md bg-[#070b14] border-l border-slate-800 p-6 overflow-y-auto flex flex-col justify-between shadow-2xl"
        >
          <div>
            {/* Drawer Header */}
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-6">
              <div>
                <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-widest block">
                  {zone.floor} • {zone.area_m2} m²
                </span>
                <h3 className="text-xl font-extrabold text-white tracking-tight mt-0.5">{zone.name}</h3>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Zone Status Banner */}
            <div className={`p-4 rounded-2xl border ${colorBadges} mb-6 flex items-center justify-between`}>
              <div className="flex items-center gap-2.5">
                <Activity className="w-5 h-5" />
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider block">Zone Status</span>
                  <span className="text-sm font-extrabold">{zone.comfort_status}</span>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold uppercase border bg-black/40">
                {zone.hvac_status}
              </span>
            </div>

            {/* Metric Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase mb-1">
                  <Thermometer className="w-4 h-4 text-emerald-400" /> Temperature
                </div>
                <span className="text-2xl font-extrabold text-white font-mono">{zone.temperature_c}°C</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase mb-1">
                  <Droplets className="w-4 h-4 text-cyan-400" /> Humidity
                </div>
                <span className="text-2xl font-extrabold text-white font-mono">{zone.humidity_pct}%</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase mb-1">
                  <ShieldCheck className="w-4 h-4 text-rose-400" /> ASHRAE PMV
                </div>
                <span className="text-2xl font-extrabold text-white font-mono">
                  {zone.pmv >= 0 ? `+${zone.pmv}` : zone.pmv}
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase mb-1">
                  <Zap className="w-4 h-4 text-amber-400" /> Cooling Load
                </div>
                <span className="text-2xl font-extrabold text-white font-mono">{zone.cooling_load_kw} kW</span>
              </div>
            </div>

            {/* Occupancy Card */}
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <UserCheck className="w-5 h-5 text-emerald-400" />
                <div>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Occupancy State</span>
                  <span className="text-sm font-extrabold text-white">{zone.occupancy_state}</span>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-mono font-bold uppercase">
                ACTIVE
              </span>
            </div>

            {/* Active Specialist Agent Recommendation */}
            {zone.agent_recommendation && (
              <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-500/30 relative overflow-hidden">
                <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase mb-2">
                  <Cpu className="w-4 h-4" /> Specialist Agent Recommendation
                </div>
                <p className="text-xs text-slate-300 font-medium leading-relaxed">
                  "{zone.agent_recommendation}"
                </p>
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 text-center">
            <button
              onClick={onClose}
              className="w-full py-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-extrabold text-xs tracking-wider uppercase transition"
            >
              Close Detail Panel
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
