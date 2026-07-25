import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { History as HistoryIcon, Download, Sparkles, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import XAIReportModal from '../components/XAIReportModal';

export default function History({ setToast }) {
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [reportLoadingId, setReportLoadingId] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await fetch('/optimize/history?limit=20');
      if (res.ok) {
        const data = await res.json();
        setHistoryList(data.history || []);
      }
    } catch (err) {
      console.error('Failed fetching history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleOpenReport = async (simId) => {
    setReportLoadingId(simId);
    if (setToast) setToast({ type: 'loading', title: 'Generating XAI Report', message: `Synthesizing decision trees for Sim #${simId}...` });

    try {
      const res = await fetch(`/optimize/explanation/${simId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedReport(data);
        setIsModalOpen(true);
        if (setToast) setToast({ type: 'success', title: 'XAI Report Ready', message: `Report generated for Sim #${simId}` });
      } else {
        throw new Error('Failed to generate report');
      }
    } catch (err) {
      console.error('Failed fetching XAI report:', err);
      if (setToast) setToast({ type: 'error', title: 'Report Failed', message: err.message });
    } finally {
      setReportLoadingId(null);
    }
  };

  const handleExportCSV = (closedLoopRunId = 1) => {
    window.open(`/analytics/export/csv/${closedLoopRunId}`, '_blank');
    if (setToast) setToast({ type: 'info', title: 'Downloading CSV Export', message: 'Downloading multi-iteration analytics CSV...' });
  };

  const handleExportJSON = (closedLoopRunId = 1) => {
    window.open(`/analytics/export/json/${closedLoopRunId}`, '_blank');
    if (setToast) setToast({ type: 'info', title: 'Downloading JSON Export', message: 'Downloading structured JSON analytics artifact...' });
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-3xl p-6 border border-slate-800 flex flex-wrap items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <HistoryIcon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Closed-Loop Optimization History & XAI Audit</h3>
            <p className="text-xs text-slate-400">Audit trail of all multi-agent consensus decisions and energy reductions</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => handleExportCSV(1)}
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-emerald-400 hover:border-emerald-500/40 transition flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" /> Export CSV
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => handleExportJSON(1)}
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-cyan-400 hover:border-cyan-500/40 transition flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" /> Export JSON
          </motion.button>
        </div>
      </motion.div>

      {/* History Table */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                <th className="pb-3 px-4">Iter #</th>
                <th className="pb-3 px-4">Sim ID</th>
                <th className="pb-3 px-4">Energy Before</th>
                <th className="pb-3 px-4">Energy After</th>
                <th className="pb-3 px-4">Savings (%)</th>
                <th className="pb-3 px-4">Final Consensus Recommendation</th>
                <th className="pb-3 px-4 text-right">XAI Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs font-mono">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-purple-400" />
                    Loading optimization records...
                  </td>
                </tr>
              ) : historyList.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    No closed loop history records yet. Execute closed loop to populate audit trail.
                  </td>
                </tr>
              ) : (
                historyList.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/50 transition">
                    <td className="py-3.5 px-4 font-bold text-purple-400">#{item.iteration}</td>
                    <td className="py-3.5 px-4 text-white">Sim #{item.simulation_id}</td>
                    <td className="py-3.5 px-4 text-slate-300">{(item.energy_before || 160).toFixed(1)} kWh</td>
                    <td className="py-3.5 px-4 text-emerald-400 font-bold">{(item.energy_after || 135).toFixed(1)} kWh</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                        -{(item.actual_savings || 15.0).toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-sans text-xs max-w-xs truncate">
                      {item.final_recommendation || 'Set cooling setpoint to 23.0°C'}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <motion.button
                        whileHover={{ scale: 1.06 }}
                        whileTap={{ scale: 0.94 }}
                        onClick={() => handleOpenReport(item.id || item.simulation_id)}
                        disabled={reportLoadingId === (item.id || item.simulation_id)}
                        className="px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-300 hover:bg-purple-500/20 text-xs font-sans font-semibold transition inline-flex items-center gap-1.5"
                      >
                        {reportLoadingId === (item.id || item.simulation_id) ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            <span>Loading...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                            <span>AI Report</span>
                          </>
                        )}
                      </motion.button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* XAI Report Modal */}
      {isModalOpen && selectedReport && (
        <XAIReportModal
          isOpen={isModalOpen}
          reportData={selectedReport}
          report={selectedReport}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </div>
  );
}
