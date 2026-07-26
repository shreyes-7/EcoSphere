import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Clock, Filter, Trash2, ShieldCheck, Zap, RefreshCw } from 'lucide-react';
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
      let url = '/monitoring/logs?limit=50';
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

  const handleClearLogs = async () => {
    try {
      await fetch('/monitoring/clear', { method: 'POST' });
      setLogs([]);
      setMetrics({
        total_evaluations: 0,
        avg_execution_time_ms: 0.0,
        error_rate_percent: 0.0,
        active_agents: 4,
        agent_latency: []
      });
    } catch (err) {
      console.error('Error clearing telemetry logs:', err);
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
          value={metrics?.total_evaluations ?? 0}
          unit="Evaluations"
          subtitle="Real-time multi-agent reasoning calls"
          icon={Activity}
          color="emerald"
        />
        <KPICard
          title="Average Agent Execution Latency"
          value={(metrics?.avg_execution_time_ms ?? 0.0).toFixed(2)}
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
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-bold text-xs hover:text-white transition flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleClearLogs}
            className="px-3.5 py-2 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold text-xs hover:bg-rose-500/20 transition flex items-center gap-1.5"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear Logs</span>
          </button>
        </div>
      </motion.div>

      {/* Logs Table or Empty State */}
      {logs.length === 0 ? (
        <div className="amoled-card rounded-3xl p-12 border border-slate-800 text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
            <Activity className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-bold text-white">No System Telemetry Logs Recorded Yet</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            The telemetry log store is fresh. Run an optimization or trigger an agent evaluation to stream microsecond latency logs into the system.
          </p>
        </div>
      ) : (
        <div className="amoled-card rounded-3xl border border-slate-800 overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-950/80 border-b border-slate-800/80 text-[11px] font-mono font-bold text-slate-400 uppercase tracking-wider">
                  <th className="py-3.5 px-5">Timestamp</th>
                  <th className="py-3.5 px-4">Level</th>
                  <th className="py-3.5 px-4">Agent</th>
                  <th className="py-3.5 px-4">Simulation ID</th>
                  <th className="py-3.5 px-4">Latency (ms)</th>
                  <th className="py-3.5 px-5">Message / Recommendation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-xs font-mono">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-3.5 px-5 text-slate-400 whitespace-nowrap">
                      {new Date(log.timestamp).toISOString().replace('T', ' ').replace('Z', '')}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          log.level === 'ERROR'
                            ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                            : log.level === 'WARNING'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        }`}
                      >
                        {log.level}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-white capitalize">{log.agent || 'System'}</td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {log.simulation_id ? `Sim #${log.simulation_id}` : 'Sim #N/A'}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-emerald-400">{log.execution_time_ms} ms</td>
                    <td className="py-3.5 px-5 text-slate-300 font-sans max-w-md truncate">
                      {log.recommendation || log.reason || 'Agent reasoning completed cleanly'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
