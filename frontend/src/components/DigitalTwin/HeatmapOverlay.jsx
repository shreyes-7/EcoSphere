import React from 'react';
import { motion } from 'framer-motion';
import { Layers, Thermometer, Zap, ShieldCheck, Leaf } from 'lucide-react';

export default function HeatmapOverlay({ heatmapData, activeMode, onSelectMode }) {
  const MODES = [
    { id: 'temperature', label: 'Temperature Heatmap', icon: Thermometer, color: 'emerald' },
    { id: 'energy', label: 'Energy Demand Heatmap', icon: Zap, color: 'cyan' },
    { id: 'comfort', label: 'Comfort (PMV) Heatmap', icon: ShieldCheck, color: 'rose' },
    { id: 'carbon', label: 'Carbon Intensity Heatmap', icon: Leaf, color: 'amber' },
  ];

  return (
    <div className="amoled-card rounded-3xl p-6 border border-slate-800/90">
      {/* Header & Mode Selectors */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800/80">
        <div>
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            <span>Interactive Thermal & Spatial Heatmap</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time spatial visualization mode: <strong className="text-cyan-300 capitalize">{activeMode}</strong>
          </p>
        </div>

        {/* Mode Selector Buttons */}
        <div className="flex flex-wrap gap-2">
          {MODES.map((m) => {
            const Icon = m.icon;
            const isActive = activeMode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => onSelectMode(m.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 border ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-lg shadow-cyan-500/10'
                    : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{m.label.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {heatmapData?.zones?.map((zone) => {
          let valDisplay = `${zone.temperature_c} °C`;
          let intensityPct = 50;

          if (activeMode === 'energy') {
            valDisplay = `${zone.cooling_load_kw} kW`;
            intensityPct = Math.min(100, (zone.cooling_load_kw / 15.0) * 100);
          } else if (activeMode === 'comfort') {
            valDisplay = `${zone.pmv} PMV`;
            intensityPct = Math.min(100, (Math.abs(zone.pmv) / 0.5) * 100);
          } else if (activeMode === 'carbon') {
            valDisplay = `0.40 kgCO2e/kWh`;
            intensityPct = 40;
          } else {
            intensityPct = Math.min(100, ((zone.temperature_c - 20.0) / 8.0) * 100);
          }

          return (
            <motion.div
              key={zone.zone_id}
              whileHover={{ scale: 1.02 }}
              className="p-5 rounded-2xl bg-slate-950 border border-slate-800 relative overflow-hidden flex flex-col justify-between h-36"
            >
              <div
                className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 via-emerald-500/10 to-transparent pointer-events-none"
                style={{ opacity: intensityPct / 100 }}
              />

              <div className="relative z-10 flex items-center justify-between">
                <span className="text-xs font-extrabold text-white">{zone.name}</span>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-black/60 text-cyan-300 border border-cyan-500/30">
                  {valDisplay}
                </span>
              </div>

              <div className="relative z-10">
                <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono mb-1">
                  <span>Intensity Scale</span>
                  <span>{Math.round(intensityPct)}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-slate-800">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 rounded-full transition-all duration-300"
                    style={{ width: `${intensityPct}%` }}
                  />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
