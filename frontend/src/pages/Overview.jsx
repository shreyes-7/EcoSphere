import React from 'react';
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
  ArrowUpRight
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';
import KPICard from '../components/KPICard';

const HOURLY_ENERGY_DATA = [
  { hour: '00:00', baseline: 140, optimized: 120, hvac: 40 },
  { hour: '04:00', baseline: 130, optimized: 110, hvac: 35 },
  { hour: '08:00', baseline: 180, optimized: 150, hvac: 65 },
  { hour: '12:00', baseline: 210, optimized: 165, hvac: 80 },
  { hour: '16:00', baseline: 195, optimized: 155, hvac: 70 },
  { hour: '20:00', baseline: 160, optimized: 130, hvac: 50 },
  { hour: '23:59', baseline: 145, optimized: 122, hvac: 42 },
];

export default function Overview({ latestSimulation, supervisorPlan, onNavigate }) {
  const electricity = latestSimulation?.electricity || 160.0;
  const hvac = latestSimulation?.hvac || 50.0;
  const pmv = latestSimulation?.pmv !== undefined ? latestSimulation?.pmv : 0.12;

  return (
    <div className="space-[#1e293b] space-y-6">
      {/* Top KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <KPICard
          title="Electricity Consumption"
          value={electricity.toFixed(1)}
          unit="kWh"
          subtitle="Baseline building demand"
          icon={Zap}
          color="emerald"
        />
        <KPICard
          title="HVAC Conditioning Load"
          value={hvac.toFixed(1)}
          unit="kWh"
          subtitle="Thermal & chiller energy"
          icon={Activity}
          color="cyan"
        />
        <KPICard
          title="Thermal Comfort (PMV)"
          value={pmv >= 0 ? `+${pmv.toFixed(2)}` : pmv.toFixed(2)}
          unit="PMV"
          subtitle="ASHRAE-55 Comfort Target: 0.0"
          icon={Thermometer}
          color="rose"
        />
        <KPICard
          title="Active AI Specialists"
          value="5"
          unit="Agents"
          subtitle="Energy, Comfort, Cost, Sustain, Supervisor"
          icon={Cpu}
          color="amber"
        />
      </div>

      {/* Main Content Grid: Chart + Supervisor Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real-time Energy Load Chart (2 cols) */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 glass-panel rounded-3xl p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-emerald-400" />
                Hourly Energy Demand Curve
              </h3>
              <p className="text-xs text-slate-400">Baseline (160 kWh) vs. Closed-Loop Strategy (120.5 kWh)</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-slate-400">
                <span className="w-3 h-3 rounded-full bg-slate-600"></span> Baseline
              </span>
              <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                <span className="w-3 h-3 rounded-full bg-emerald-400"></span> AI Optimized (-15.4%)
              </span>
            </div>
          </div>

          <div className="h-72 w-full">
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
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }}
                />
                <Area type="monotone" dataKey="baseline" stroke="#64748b" strokeWidth={2} fillOpacity={1} fill="url(#baselineGrad)" />
                <Area type="monotone" dataKey="optimized" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#optimizedGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Supervisor Consensus Plan (1 col) */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-panel rounded-3xl p-6 border border-emerald-500/20 flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" /> Supervisor AI Plan
              </span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[11px] font-mono font-semibold">
                High Priority
              </span>
            </div>

            <h4 className="text-lg font-bold text-white mb-2">
              "{supervisorPlan?.final_recommendation || 'Reduce discretionary energy use during high-carbon operating periods.'}"
            </h4>

            <p className="text-xs text-slate-400 leading-relaxed mb-6">
              Coordinated consensus between Energy, Comfort, Cost, and Sustainability specialist agents enforcing ASHRAE-55 comfort guardrails.
            </p>

            {/* Specialist Agents Mini Grid */}
            <div className="space-y-2.5">
              <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                <span className="text-slate-300 font-medium flex items-center gap-2">
                  <Zap className="w-3.5 h-3.5 text-emerald-400" /> Energy Specialist
                </span>
                <span className="text-slate-400 font-mono">Low Priority</span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                <span className="text-slate-300 font-medium flex items-center gap-2">
                  <Thermometer className="w-3.5 h-3.5 text-rose-400" /> Comfort Specialist
                </span>
                <span className="text-emerald-400 font-mono">Satisfied (0.12 PMV)</span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                <span className="text-slate-300 font-medium flex items-center gap-2">
                  <Leaf className="w-3.5 h-3.5 text-amber-400" /> Sustainability Agent
                </span>
                <span className="text-amber-400 font-semibold font-mono">0.400 kgCO2e/kWh</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onNavigate('optimization')}
            className="w-full mt-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-white flex items-center justify-center gap-2 transition"
          >
            <span>Launch Multi-Agent Closed Loop</span>
            <ArrowUpRight className="w-4 h-4 text-emerald-400" />
          </button>
        </motion.div>
      </div>
    </div>
  );
}
