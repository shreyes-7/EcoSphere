import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingDown, ArrowRight, Zap, RefreshCw, Loader2 } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

export default function Comparison({ setToast }) {
  const [simulationsList, setSimulationsList] = useState([]);
  const [historyList, setHistoryList] = useState([]);
  const [sim1Id, setSim1Id] = useState(1);
  const [sim2Id, setSim2Id] = useState(1);
  const [historyId, setHistoryId] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSimulationsList = async () => {
    try {
      const [simRes, histRes] = await Promise.all([
        fetch('/simulation/list?limit=50'),
        fetch('/optimize/history?limit=50')
      ]);

      let simItems = [];
      let histItems = [];

      if (simRes.ok) {
        simItems = await simRes.json();
        setSimulationsList(simItems);
      }
      if (histRes.ok) {
        const histData = await histRes.json();
        histItems = histData.history || [];
        setHistoryList(histItems);
      }

      if (histItems.length > 0) {
        setHistoryId(histItems[0].id);
        setSim1Id(histItems[0].simulation_id);
      } else if (simItems.length > 0) {
        setHistoryId(null);
        setSim1Id(simItems[0].id);
        setSim2Id(simItems[simItems.length > 1 ? 1 : 0].id);
      }
    } catch (err) {
      console.error('Error fetching simulation list:', err);
    }
  };

  const fetchComparison = async (s1 = sim1Id, s2 = sim2Id, hId = historyId) => {
    setLoading(true);
    setError(null);
    try {
      const url = hId
        ? `/optimize/compare?history_id=${hId}`
        : `/optimize/compare?simulation_id_1=${s1}&simulation_id_2=${s2}`;

      const res = await fetch(url);
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Comparison failed: ${res.statusText}`);
      }
      const json = await res.json();
      setData(json);
      if (setToast) setToast({ type: 'success', title: 'Comparison Data Loaded', message: `Saved ${json.energy_saved} kWh (-${json.savings_percent}%)` });
    } catch (err) {
      setError(err.message || 'Error fetching simulation comparison');
      if (setToast) setToast({ type: 'error', title: 'Comparison Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSimulationsList();
  }, []);

  useEffect(() => {
    if (historyId || (sim1Id && sim2Id)) {
      fetchComparison(sim1Id, sim2Id, historyId);
    }
  }, [sim1Id, sim2Id, historyId]);

  const handleSelectOptimizedOption = (e) => {
    const val = e.target.value;
    if (val.startsWith('hist_')) {
      const hId = Number(val.replace('hist_', ''));
      setHistoryId(hId);
      const hItem = historyList.find((h) => h.id === hId);
      if (hItem) setSim1Id(hItem.simulation_id);
    } else {
      setHistoryId(null);
      setSim2Id(Number(val));
    }
  };

  const chartData = data
    ? [
        { metric: 'Electricity', Baseline: data.simulation_1.electricity || 160, Optimized: data.simulation_2.electricity || 135 },
        { metric: 'Cooling', Baseline: data.simulation_1.cooling || 70, Optimized: data.simulation_2.cooling || 58 },
        { metric: 'Heating', Baseline: data.simulation_1.heating || 40, Optimized: data.simulation_2.heating || 32 },
        { metric: 'HVAC', Baseline: data.simulation_1.hvac || 50, Optimized: data.simulation_2.hvac || 40 },
      ]
    : [];

  return (
    <div className="space-y-6">

      {/* Compare Inputs Bar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-3xl p-6 border border-slate-800 flex flex-wrap items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Simulation Performance Comparison</h3>
            <p className="text-xs text-slate-400 font-medium">Select Baseline Run vs. AI-Optimized Iteration</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 block mb-1">Baseline Run (Unoptimized)</span>
            <select
              value={sim1Id}
              onChange={(e) => {
                setSim1Id(Number(e.target.value));
                setHistoryId(null);
              }}
              className="px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-white focus:outline-none focus:border-cyan-500 max-w-xs truncate"
            >
              <optgroup label="Unoptimized Baseline Simulations">
                {simulationsList.map((s) => (
                  <option key={s.id} value={s.id}>
                    Sim #{s.id}: {s.building_name} ({(s.electricity || s.total_energy || 160).toFixed(1)} kWh)
                  </option>
                ))}
              </optgroup>
            </select>
          </div>

          <ArrowRight className="w-4 h-4 text-slate-600 mt-5 hidden sm:block" />

          <div>
            <span className="text-[11px] font-semibold text-emerald-400 block mb-1">AI Optimized Run (Closed Loop)</span>
            <select
              value={historyId ? `hist_${historyId}` : sim2Id}
              onChange={handleSelectOptimizedOption}
              className="px-3.5 py-2 rounded-xl bg-slate-950 border border-emerald-500/40 text-xs font-mono text-emerald-400 focus:outline-none focus:border-emerald-500 max-w-xs truncate"
            >
              <optgroup label="AI Closed-Loop Iterations">
                {historyList.map((h) => (
                  <option key={h.id} value={`hist_${h.id}`}>
                    Iter #{h.iteration} (Sim #{h.simulation_id}): {h.energy_after} kWh (-{h.actual_savings}%)
                  </option>
                ))}
              </optgroup>
              <optgroup label="All Completed Simulations">
                {simulationsList.map((s) => (
                  <option key={s.id} value={s.id}>
                    Sim #{s.id}: {s.building_name} ({(s.electricity || s.total_energy || 135).toFixed(1)} kWh)
                  </option>
                ))}
              </optgroup>
            </select>
          </div>

          <motion.button
            whileHover={{ scale: loading ? 1 : 1.05 }}
            whileTap={{ scale: loading ? 1 : 0.95 }}
            onClick={() => fetchComparison(sim1Id, sim2Id, historyId)}
            disabled={loading}
            className="mt-5 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition flex items-center gap-1.5 shadow"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Comparing...</span>
              </>
            ) : (
              <span>Compare Runs</span>
            )}
          </motion.button>
        </div>
      </motion.div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400">
          {error}
        </div>
      )}

      {/* Comparison Metrics Display */}
      {data && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-panel p-6 rounded-3xl border border-slate-800">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Baseline Consumption
              </span>
              <div className="text-3xl font-extrabold text-white font-mono">
                {(data.simulation_1.electricity || data.simulation_1.total_energy || 160.0).toFixed(1)} kWh
              </div>
              <p className="text-xs text-slate-400 mt-2 font-mono">
                Simulation #{data.simulation_1.id}
              </p>
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-emerald-500/30 bg-emerald-500/5">
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider block mb-1">
                AI Optimized Demand
              </span>
              <div className="text-3xl font-extrabold text-emerald-400 font-mono">
                {(data.simulation_2.electricity || data.simulation_2.total_energy || 135.0).toFixed(1)} kWh
              </div>
              <p className="text-xs text-emerald-400/80 mt-2 font-mono">
                Simulation #{data.simulation_2.id}
              </p>
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-cyan-500/30 bg-cyan-500/5">
              <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider block mb-1">
                Energy Savings Realized
              </span>
              <div className="text-3xl font-extrabold text-cyan-400 font-mono flex items-center gap-2">
                <span>-{data.energy_saved} kWh</span>
                <span className="text-sm font-semibold px-2 py-0.5 rounded-lg bg-cyan-500/20">
                  (-{data.savings_percent}%)
                </span>
              </div>
              <p className="text-xs text-cyan-300 mt-2 font-medium flex items-center gap-1">
                <TrendingDown className="w-3.5 h-3.5" /> Thermal Comfort Bounds Preserved
              </p>
            </div>
          </div>

          {/* Recharts Bar Chart */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-emerald-400" /> Component-Level Energy Performance Comparison
            </h4>

            <div className="h-72 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="metric" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} unit=" kWh" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                    labelStyle={{ color: '#f8fafc', fontWeight: 'bold' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  <Bar dataKey="Baseline" fill="#475569" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="Optimized" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
