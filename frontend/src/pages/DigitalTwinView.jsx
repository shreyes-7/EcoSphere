import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Layers, Thermometer, Zap, ShieldCheck, RefreshCw } from 'lucide-react';
import KPICard from '../components/KPICard';
import DigitalTwinFloorPlan from '../components/DigitalTwin/DigitalTwinFloorPlan';
import HeatmapOverlay from '../components/DigitalTwin/HeatmapOverlay';
import ZoneDetailDrawer from '../components/DigitalTwin/ZoneDetailDrawer';

export default function DigitalTwinView({ setToast }) {
  const [digitalTwinState, setDigitalTwinState] = useState(null);
  const [heatmapData, setHeatmapData] = useState(null);
  const [heatmapMode, setHeatmapMode] = useState('temperature');
  const [selectedZone, setSelectedZone] = useState(null);
  const [activeTab, setActiveTab] = useState('floorplan'); // 'floorplan' | 'heatmap'
  const [loading, setLoading] = useState(true);

  const fetchDigitalTwinData = async () => {
    setLoading(true);
    try {
      const [stateRes, heatmapRes] = await Promise.all([
        fetch('/digital-twin/state'),
        fetch(`/digital-twin/heatmap?mode=${heatmapMode}`)
      ]);

      if (stateRes.ok) {
        const data = await stateRes.json();
        setDigitalTwinState(data);
      }
      if (heatmapRes.ok) {
        const hmData = await heatmapRes.json();
        setHeatmapData(hmData);
      }
    } catch (err) {
      console.error("Failed to fetch Digital Twin state:", err);
      if (setToast) setToast({ message: 'Failed to connect to Digital Twin backend API', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDigitalTwinData();
  }, [heatmapMode]);

  const zones = digitalTwinState?.zones || [];

  return (
    <div className="space-y-8 amoled-grid-bg min-h-full pb-8">
      {/* Header Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden amoled-card rounded-3xl p-6 lg:p-8 border border-emerald-500/30"
      >
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2.5 mb-3">
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-[11px] font-mono font-bold uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                AI Digital Twin Active
              </span>
              <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-[11px] font-mono font-semibold">
                Building: {digitalTwinState?.building_name || 'Commercial Test Facility'}
              </span>
            </div>

            <h1 className="text-2xl lg:text-3xl font-black text-white tracking-tight">
              Interactive Building Digital Twin & Heatmap
            </h1>
            <p className="text-xs lg:text-sm text-slate-400 max-w-2xl mt-1.5">
              Real-time thermal zone representation, ASHRAE-55 PMV compliance, and spatial load distribution.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchDigitalTwinData}
              className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
              title="Refresh State"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>

            {/* View Switcher */}
            <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/90 border border-slate-800 text-xs font-medium">
              <button
                onClick={() => setActiveTab('floorplan')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'floorplan'
                    ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Floor Plan
              </button>
              <button
                onClick={() => setActiveTab('heatmap')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'heatmap'
                    ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Spatial Heatmap
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Top Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <KPICard
          title="Total Monitored Zones"
          value={digitalTwinState?.total_zones || 6}
          unit="Zones"
          subtitle="Full thermal zone coverage"
          icon={Layers}
          color="emerald"
          trend="100% Online"
        />
        <KPICard
          title="Mean Building Temp"
          value={(digitalTwinState?.average_temperature_c || 23.0).toFixed(1)}
          unit="°C"
          subtitle="Average dry-bulb temperature"
          icon={Thermometer}
          color="cyan"
          trend="Optimal"
        />
        <KPICard
          title="Comfort Compliance"
          value={(digitalTwinState?.comfort_compliance_pct || 100.0).toFixed(0)}
          unit="%"
          subtitle="Zones meeting PMV [-0.5, +0.5]"
          icon={ShieldCheck}
          color="rose"
          trend="ASHRAE-55"
        />
        <KPICard
          title="Total Cooling Rate"
          value={(digitalTwinState?.total_cooling_kw || 50.0).toFixed(1)}
          unit="kW"
          subtitle="Aggregated thermal load"
          icon={Zap}
          color="amber"
          trend="Balanced"
        />
      </div>

      {/* Main View Area */}
      {activeTab === 'floorplan' ? (
        <DigitalTwinFloorPlan zones={zones} onSelectZone={setSelectedZone} />
      ) : (
        <HeatmapOverlay
          heatmapData={heatmapData}
          activeMode={heatmapMode}
          onSelectMode={setHeatmapMode}
        />
      )}

      {/* Zone Detail Drawer Modal */}
      <ZoneDetailDrawer zone={selectedZone} onClose={() => setSelectedZone(null)} />
    </div>
  );
}
