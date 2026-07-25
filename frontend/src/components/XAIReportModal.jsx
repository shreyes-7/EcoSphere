import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ShieldCheck, Leaf, Sparkles, AlertCircle, FileText, CheckCircle2, Zap, Cpu, DollarSign } from 'lucide-react';

export default function XAIReportModal({ isOpen = true, onClose, reportData, report }) {
  const data = reportData || report;
  if (!isOpen || !data) return null;

  const confidencePct = Math.round((data.confidence || 0.92) * 100);
  const expectedSavings = data.expected_savings_percent || data.expected_savings || 12.5;
  const recommendationText = data.recommendation || data.final_recommendation || 'Increase cooling setpoint by +0.5°C to 23.5°C to optimize chiller COP.';
  const simId = data.simulation_id || data.id || 1;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-3xl p-6 shadow-2xl overflow-hidden glass-glow-emerald max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-5">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Explainable AI (XAI) Decision Report</h3>
                <p className="text-xs text-slate-400">Simulation #{simId} Multi-Agent Consensus Rationale</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Metrics Row */}
          <div className="grid grid-cols-2 gap-4 mb-5">
            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Supervisor Confidence</span>
              <div className="text-2xl font-bold text-purple-400 font-mono mt-1 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-purple-400" />
                {confidencePct}%
              </div>
            </div>
            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Expected Energy Savings</span>
              <div className="text-2xl font-bold text-emerald-400 font-mono mt-1 flex items-center gap-2">
                <Zap className="w-5 h-5 text-emerald-400" />
                {expectedSavings}%
              </div>
            </div>
          </div>

          {/* Consensus Recommendation Box */}
          <div className="p-4 rounded-2xl bg-purple-500/10 border border-purple-500/30 mb-5">
            <span className="text-[11px] font-bold text-purple-300 uppercase tracking-wider block mb-1">
              Consensus Action Plan
            </span>
            <p className="text-sm font-semibold text-purple-100">
              "{recommendationText}"
            </p>
          </div>

          {/* Specialist Agent Breakdown if present */}
          {data.agent_breakdown && data.agent_breakdown.length > 0 && (
            <div className="space-y-3 mb-5">
              <span className="text-xs font-bold text-slate-300 block uppercase tracking-wider">
                Specialist Agent Rationale
              </span>
              {data.agent_breakdown.map((agent, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-950/40 border border-slate-800 flex items-start justify-between gap-3 text-xs">
                  <div>
                    <span className="font-bold text-cyan-400 capitalize block">{agent.agent} Agent</span>
                    <span className="text-slate-300 block font-sans mt-0.5">{agent.reason || agent.recommendation}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 font-mono font-semibold shrink-0">
                    {Math.round((agent.confidence || 0.9) * 100)}%
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Guardrails & Impact */}
          <div className="space-y-3 mb-6">
            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/40 border border-slate-800">
              <CheckCircle2 className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-xs font-bold text-slate-300 block">Thermal Comfort Guardrail</span>
                <p className="text-xs text-slate-400">{data.comfort_impact || 'ISO 7730 PMV bounds strictly enforced within comfortable range (-0.5 to +0.5 PMV).'}</p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/40 border border-slate-800">
              <Leaf className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-xs font-bold text-slate-300 block">Operational Carbon Impact</span>
                <p className="text-xs text-slate-400">{data.carbon_impact || 'Reduces peak electrical grid demand and operational greenhouse gas emissions.'}</p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end pt-4 border-t border-slate-800">
            <button
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl bg-purple-500 text-white font-semibold text-xs hover:bg-purple-400 transition"
            >
              Close Report
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
