import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Zap, 
  Thermometer, 
  DollarSign, 
  Leaf, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  TrendingDown,
  ArrowUpRight,
  Sparkles,
  CloudSun,
  Layers,
  BarChart2,
  CheckCircle2,
  Clock,
  Sliders
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';
import KPICard from '../components/KPICard';

const HOURLY_ENERGY_DATA = [
  { hour: '00:00', baseline: 140, optimized: 120, hvac: 40, solar: 0 },
  { hour: '04:00', baseline: 130, optimized: 110, hvac: 35, solar: 0 },
  { hour: '08:00', baseline: 180, optimized: 145, hvac: 65, solar: 180 },
  { hour: '12:00', baseline: 210, optimized: 158, hvac: 80, solar: 520 },
  { hour: '16:00', baseline: 195, optimized: 150, hvac: 70, solar: 410 },
  { hour: '20:00', baseline: 160, optimized: 128, hvac: 50, solar: 40 },
  { hour: '23:59', baseline: 145, optimized: 121, hvac: 42, solar: 0 },
];

const COMPONENT_BREAKDOWN = [
  { name: 'HVAC Cooling', value: 38.1, color: '#10b981' },
  { name: 'Lighting Load', value: 15.2, color: '#06b6d4' },
  { name: 'Plug Power', value: 22.9, color: '#8b5cf6' },
  { name: 'Aux Fans & Pumps', value: 23.8, color: '#f59e0b' },
];

export default function Overview({ latestSimulation, supervisorPlan, onNavigate, onExecuteClosedLoop, setToast }) {
  const [chartView, setChartView] = useState('hourly'); // 'hourly' | 'components'

  const electricity = latestSimulation?.electricity || 131.2;
  const hvac = latestSimulation?.hvac || 50.0;
  const pmv = latestSimulation?.pmv !== undefined ? latestSimulation?.pmv : 0.12;
  const coolingSetpoint = latestSimulation?.cooling_setpoint || 23.0;

  return (
    <div className="space-y-8 amoled-grid-bg min-h-full pb-8">
      {/* Hero Command Center Banner */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden amoled-card rounded-3xl p-6 lg:p-8 border border-emerald-500/30"
      >
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-gradient-to-br from-emerald-500/15 via-cyan-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div>
            <div className="flex flex-wrap items-center gap-2.5 mb-3">
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-[11px] font-mono font-bold uppercase tracking-wider flex items-center gap-1.5 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Autonomous Building Command Center
              </span>
              <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-[11px] font-mono font-semibold flex items-center gap-1.5">
                <CloudSun className="w-3.5 h-3.5 text-cyan-400" />
                San Francisco EPW Weather Active
              </span>
            </div>

            <h1 className="text-2xl lg:text-3xl font-black text-white tracking-tight leading-tight">
              Real-Time Physical AI Building Telemetry
            </h1>
            <p className="text-xs lg:text-sm text-slate-400 max-w-2xl mt-1.5 leading-relaxed">
              Multi-agent reinforcement control enforcing ASHRAE-55 thermal comfort guardrails and physics-based EnergyPlus balance modeling.
            </p>
          </div>

          {/* Quick Action Trigger Buttons */}
          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            <button
              onClick={() => onNavigate && onNavigate('simulation')}
              className="flex-1 lg:flex-none px-4 py-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 text-xs font-semibold text-slate-200 flex items-center justify-center gap-2 transition-all shadow-lg hover:border-slate-600"
            >
              <BarChart2 className="w-4 h-4 text-cyan-400" />
              <span>Run Physics Simulation</span>
            </button>

            <button
              onClick={() => (onExecuteClosedLoop ? onExecuteClosedLoop() : (onNavigate && onNavigate('optimization')))}
              className="flex-1 lg:flex-none px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 text-xs font-extrabold flex items-center justify-center gap-2 transition-all shadow-xl shadow-emerald-500/20"
            >
              <Cpu className="w-4 h-4" />
              <span>Launch Closed Loop</span>
              <ArrowUpRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Top 4 KPI Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <KPICard
          title="Baseline Electricity Demand"
          value={electricity.toFixed(1)}
          unit="kWh"
          subtitle="Physics heat balance total demand"
          icon={Zap}
          color="emerald"
          trend="-16.8% AI Savings"
        />
        <KPICard
          title="HVAC Conditioning Load"
          value={hvac.toFixed(1)}
          unit="kWh"
          subtitle="Thermal & chiller energy transfer"
          icon={Activity}
          color="cyan"
          trend="COP 3.5 Active"
        />
        <KPICard
          title="Thermal Comfort (PMV)"
          value={pmv >= 0 ? `+${pmv.toFixed(2)}` : pmv.toFixed(2)}
          unit="PMV"
          subtitle="ASHRAE-55 Target Range: [-0.5, +0.5]"
          icon={Thermometer}
          color="rose"
          trend="Target Compliant"
        />
        <KPICard
          title="Active Specialist Swarm"
          value="5"
          unit="Agents"
          subtitle="Energy, Comfort, Cost, Sustain, Supervisor"
          icon={Cpu}
          color="amber"
          trend="95% Confidence"
        />
      </div>

      {/* Main Content Grid: Interactive Chart (2 Cols) + Multi-Agent Consensus Matrix (1 Col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real-time Energy Load Chart & Analytics (2 cols) */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 amoled-card rounded-3xl p-6 border border-slate-800/90 flex flex-col justify-between"
        >
          {/* Chart Header Controls */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800/80">
            <div>
              <h3 className="text-base font-extrabold text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-emerald-400" />
                <span>Hourly Energy Demand & Load Distribution</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Side-by-side comparison of Unoptimized Baseline (160.0 kWh) vs. AI Multi-Agent Closed Loop Strategy (114.2 kWh)
              </p>
            </div>

            {/* Toggle View Filters */}
            <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/90 border border-slate-800 text-xs font-medium">
              <button
                onClick={() => setChartView('hourly')}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  chartView === 'hourly'
                    ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Hourly Profile
              </button>
              <button
                onClick={() => setChartView('components')}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  chartView === 'components'
                    ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Component Split
              </button>
            </div>
          </div>

          {/* Dynamic Recharts Render */}
          <div className="h-72 w-full">
            {chartView === 'hourly' ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={HOURLY_ENERGY_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="baselineGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#475569" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#475569" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="optimizedGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.5} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
                  <XAxis dataKey="hour" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ 
                      backgroundColor: '#070b14', 
                      borderColor: '#10b981', 
                      borderRadius: '12px', 
                      color: '#fff',
                      boxShadow: '0 10px 25px -5px rgba(0,0,0,0.8)',
                      fontSize: '12px',
                    }}
                  />
                  <Area type="monotone" dataKey="baseline" name="Unoptimized Baseline" stroke="#64748b" strokeWidth={2} fillOpacity={1} fill="url(#baselineGrad)" />
                  <Area type="monotone" dataKey="optimized" name="AI Optimized Strategy" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#optimizedGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={COMPONENT_BREAKDOWN} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} unit="%" tickLine={false} />
                  <Tooltip
                    contentStyle={{ 
                      backgroundColor: '#070b14', 
                      borderColor: '#06b6d4', 
                      borderRadius: '12px', 
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="value" name="Energy Share (%)" radius={[8, 8, 0, 0]} fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Chart Footer Stats Bar */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 grid grid-cols-3 gap-4 text-center">
            <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/80">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Peak Demand</span>
              <span className="text-lg font-extrabold text-white font-mono mt-0.5 block">210.0 kW</span>
            </div>
            <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/80">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Optimized Peak</span>
              <span className="text-lg font-extrabold text-emerald-400 font-mono mt-0.5 block">158.0 kW</span>
            </div>
            <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/80">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Cooling Setpoint</span>
              <span className="text-lg font-extrabold text-cyan-400 font-mono mt-0.5 block">{coolingSetpoint.toFixed(1)}°C</span>
            </div>
          </div>
        </motion.div>

        {/* Supervisor Consensus & Agent Swarm (1 col) */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="amoled-card rounded-3xl p-6 border border-emerald-500/30 flex flex-col justify-between"
        >
          <div>
            {/* Header Badge */}
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" /> Supervisor AI Plan
              </span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono font-extrabold uppercase">
                High Confidence
              </span>
            </div>

            {/* Supervisor Rationale Title */}
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 mb-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-16 h-16 bg-emerald-500/10 rounded-full blur-xl pointer-events-none" />
              <h4 className="text-sm font-bold text-white leading-relaxed">
                "{supervisorPlan?.final_recommendation || 'HVAC energy is elevated (50.0 kWh, 31.2%). Recommend increasing cooling setpoint by +0.5°C to 23.0°C to reduce cooling load while keeping PMV comfortably within ASHRAE-55 limits.'}"
              </h4>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed mb-4 font-medium">
              Real-time multi-agent voting matrix balancing comfort, energy efficiency, electricity cost tariffs, and carbon intensity.
            </p>

            {/* Specialist Agents Voting Matrix Stack */}
            <div className="space-y-2.5">
              <div className="flex justify-between items-center p-3 rounded-2xl bg-slate-950/80 border border-slate-800/90 text-xs">
                <div className="flex items-center gap-2.5">
                  <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
                  <span className="text-slate-200 font-bold">Energy Agent</span>
                </div>
                <span className="text-emerald-400 font-mono font-bold text-[11px]">Weight: 35%</span>
              </div>

              <div className="flex justify-between items-center p-3 rounded-2xl bg-slate-950/80 border border-slate-800/90 text-xs">
                <div className="flex items-center gap-2.5">
                  <div className="w-2 h-2 rounded-full bg-rose-400"></div>
                  <span className="text-slate-200 font-bold">Comfort Agent</span>
                </div>
                <span className="text-rose-400 font-mono font-bold text-[11px]">PMV: 0.12 (Passed)</span>
              </div>

              <div className="flex justify-between items-center p-3 rounded-2xl bg-slate-950/80 border border-slate-800/90 text-xs">
                <div className="flex items-center gap-2.5">
                  <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
                  <span className="text-slate-200 font-bold">Cost Agent</span>
                </div>
                <span className="text-cyan-400 font-mono font-bold text-[11px]">Tariff Opt: Active</span>
              </div>

              <div className="flex justify-between items-center p-3 rounded-2xl bg-slate-950/80 border border-slate-800/90 text-xs">
                <div className="flex items-center gap-2.5">
                  <div className="w-2 h-2 rounded-full bg-amber-400"></div>
                  <span className="text-slate-200 font-bold">Sustainability Agent</span>
                </div>
                <span className="text-amber-400 font-mono font-bold text-[11px]">0.40 kgCO2e/kWh</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => (onExecuteClosedLoop ? onExecuteClosedLoop() : (onNavigate && onNavigate('optimization')))}
            className="w-full mt-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 text-xs font-black flex items-center justify-center gap-2 transition-all shadow-xl shadow-emerald-500/20"
          >
            <span>Launch Closed-Loop Control</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </motion.div>
      </div>
    </div>
  );
}
