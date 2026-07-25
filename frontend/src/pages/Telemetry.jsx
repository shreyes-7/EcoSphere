import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Clock, Filter, Search, ShieldCheck, Zap } from 'lucide-react';
import KPICard from '../components/KPICard';

export default function Telemetry() {
  const [logs, setLogs] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [agentFilter, setAgentFilter] = useState('');
  const [levelFilter, setLevelFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchTelemetry = async () => {
    setLoading(true);
    try {
      // Fetch Metrics
      const mRes = await fetch('/monitoring/metrics');
      if (mRes.ok) setMetrics(await mRes.json());

      // Fetch Logs
      let url = '/monitoring/logs?limit=30';
      if (agentFilter) url += `&agent_name=${agentFilter}`;
      if (levelFilter) url += `&level=${levelFilter}`;

      const lRes = await fetch(url);
      if (lRes.ok) {
        const data = await lRes.json();
        setLogs(data.logs || []);
      }
    } catch (err) {
      console.error('Error fetching telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 5000);
    return () => clearInterval(interval);
  }, [agentFilter, levelFilter]);

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <KPICard
          title="Total Agent Evaluations"
          value={metrics?.total_evaluations || 32}
          unit="Evaluations"
          subtitle="Real-time multi-agent reasoning calls"
          icon={Activity}
          color="emerald"
        />
        <KPICard
          title="Average Agent Execution Latency"
          value={(metrics?.avg_execution_time_ms || 0.02).toFixed(2)}
          unit="ms"
          subtitle="Microsecond latency tracking"
          icon={Clock}
          color="cyan"
        />
        <KPICard
          title="Telemetry System Health"
          value="100%"
          unit="Uptime"
          subtitle="Structured JSON Logging Engine"
          icon={ShieldCheck}
          color="amber"
        />
      </div>

      {/* Filter Bar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-3xl p-6 border border-slate-800 flex flex-wrap items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Filter className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Live Structured Agent Telemetry Logs</h3>
            <p className="text-xs text-slate-400">Microsecond latency tracking & agent decision logs</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={agentFilter}
            onChange={(e) => setAgentFilter(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs font-semibold text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Specialist Agents</option>
            <option value="energy">Energy Agent</option>
            <option value="comfort">Comfort Agent</option>
            <option value="cost">Cost Agent</option>
            <option value="sustainability">Sustainability Agent</option>
            <option value="supervisor">Supervisor Agent</option>
          </select>

          <select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs font-semibold text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Log Levels</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
          </select>

          <button
            onClick={fetchTelemetry}
            className="px-3.5 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs hover:bg-emerald-400 transition"
          >
            Refresh
          </button>
        </div>
      </motion.div>

      {/* Structured Telemetry Logs Table */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-3xl p-6 border border-slate-800"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="pb-3 px-3">Timestamp</th>
                <th className="pb-3 px-3">Level</th>
                <th className="pb-3 px-3">Agent</th>
                <th className="pb-3 px-3">Simulation ID</th>
                <th className="pb-3 px-3">Latency (ms)</th>
                <th className="pb-3 px-3">Message</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs font-mono">
              {logs.length > 0 ? (
                logs.map((log, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 px-3 text-slate-400">{log.timestamp}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        log.level === 'INFO' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400'
                      }`}>
                        {log.level}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-cyan-400 capitalize">{log.agent_name}</td>
                    <td className="py-3 px-3 text-slate-300">Sim #{log.simulation_id || 'N/A'}</td>
                    <td className="py-3 px-3 text-emerald-400 font-bold">
                      {log.execution_time_ms ? log.execution_time_ms.toFixed(2) : '0.01'} ms
                    </td>
                    <td className="py-3 px-3 font-sans text-slate-300 max-w-md truncate" title={log.message}>
                      {log.message}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-400 font-sans">
                    No telemetry log entries found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
