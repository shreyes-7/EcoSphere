import React from 'react';
import { motion } from 'framer-motion';
import { Thermometer, Activity, UserCheck, Zap } from 'lucide-react';

export default function DigitalTwinFloorPlan({ zones, onSelectZone }) {
  const getColorStyles = (colorCode) => {
    switch (colorCode) {
      case 'green':
        return 'bg-emerald-950/30 border-emerald-500/40 hover:border-emerald-400 text-emerald-300 shadow-emerald-500/10';
      case 'yellow':
        return 'bg-yellow-950/30 border-yellow-500/40 hover:border-yellow-400 text-yellow-300 shadow-yellow-500/10';
      case 'orange':
        return 'bg-orange-950/30 border-orange-500/40 hover:border-orange-400 text-orange-300 shadow-orange-500/10';
      case 'red':
        return 'bg-rose-950/30 border-rose-500/40 hover:border-rose-400 text-rose-300 shadow-rose-500/10';
      case 'blue':
        return 'bg-cyan-950/30 border-cyan-500/40 hover:border-cyan-400 text-cyan-300 shadow-cyan-500/10';
      default:
        return 'bg-slate-900/40 border-slate-700/50 hover:border-slate-500 text-slate-300';
    }
  };

  return (
    <div className="relative amoled-card rounded-3xl p-6 border border-slate-800/90 overflow-hidden">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
        <div>
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            <span>Commercial Test Facility — Floor Plan Layout</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Interactive thermal zones derived from backend simulation heat balance metrics
          </p>
        </div>

        {/* Legend */}
        <div className="hidden lg:flex items-center gap-3 text-[11px] font-mono">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> Comfortable
          </span>
          <span className="flex items-center gap-1.5 text-yellow-400">
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-400"></span> Approaching
          </span>
          <span className="flex items-center gap-1.5 text-rose-400">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span> Violation
          </span>
        </div>
      </div>

      {/* Grid Floorplan Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {zones.map((zone) => {
          const style = getColorStyles(zone.color_code);
          return (
            <motion.div
              key={zone.zone_id}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSelectZone(zone)}
              className={`cursor-pointer rounded-2xl p-5 border backdrop-blur-md transition-all duration-200 shadow-xl ${style}`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-black/40 border border-white/10">
                  {zone.floor}
                </span>
                <span className="text-[10px] font-mono font-extrabold uppercase px-2 py-0.5 rounded bg-black/40 border border-white/10">
                  {zone.hvac_status}
                </span>
              </div>

              <h4 className="text-sm font-extrabold text-white mb-3 line-clamp-1">{zone.name}</h4>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="flex items-center gap-2">
                  <Thermometer className="w-4 h-4 opacity-80" />
                  <span className="font-mono font-bold text-white">{zone.temperature_c}°C</span>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 opacity-80" />
                  <span className="font-mono font-bold text-white">{zone.cooling_load_kw} kW</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-[11px]">
                <span className="font-semibold text-slate-300">PMV: <strong className="font-mono text-white">{zone.pmv}</strong></span>
                <span className="font-bold uppercase tracking-wider">{zone.comfort_status}</span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
