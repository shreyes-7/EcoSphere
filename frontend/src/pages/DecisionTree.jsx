import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { GitCommit, ShieldCheck, Cpu, Zap, Thermometer, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import KPICard from '../components/KPICard';

export default function DecisionTree({ setToast }) {
  const [decisionFlow, setDecisionFlow] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDecisionTree = async () => {
    setLoading(true);
    try {
      const res = await fetch('/xai/decision-tree');
      if (res.ok) {
        const data = await res.json();
        setDecisionFlow(data);
      }
    } catch (err) {
      console.error("Failed to fetch decision tree:", err);
      if (setToast) setToast({ message: 'Failed to load Explainable AI decision tree', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisionTree();
  }, []);

  const rootNode = decisionFlow?.root_node;
  const supervisorNode = rootNode?.children?.[0];
  const agentNodes = supervisorNode?.children || [];
  const conflicts = decisionFlow?.conflicts || [];

  return (
    <div className="space-y-8 amoled-grid-bg min-h-full pb-8">
      {/* Header Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden amoled-card rounded-3xl p-6 lg:p-8 border border-emerald-500/30"
      >
        <div className="flex items-center justify-between relative z-10">
          <div>
            <div className="flex items-center gap-2.5 mb-3">
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-[11px] font-mono font-bold uppercase tracking-wider">
                Explainable AI (XAI) Protocol
              </span>
              <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-[11px] font-mono font-semibold">
                Iteration #{decisionFlow?.iteration || 1} Decision Flow
              </span>
            </div>

            <h1 className="text-2xl lg:text-3xl font-black text-white tracking-tight">
              Live Multi-Agent Decision Tree & Rationale
            </h1>
            <p className="text-xs lg:text-sm text-slate-400 max-w-2xl mt-1.5">
              Transparent, step-by-step reasoning hierarchy showing agent votes, conflict resolution, and supervisor consensus.
            </p>
          </div>

          <button
            onClick={fetchDecisionTree}
            className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </motion.div>

      {/* Decision Tree Hierarchy Cards */}
      <div className="space-y-6">
        {/* Root Node */}
        {rootNode && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="amoled-card rounded-3xl p-6 border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-300 text-xs font-mono font-bold uppercase">
                {rootNode.category} Node
              </span>
              <span className="text-xs font-mono text-emerald-400 font-bold">Confidence: {(rootNode.confidence * 100).toFixed(0)}%</span>
            </div>
            <h3 className="text-lg font-black text-white mb-1">{rootNode.title}</h3>
            <p className="text-xs text-slate-300 font-medium">{rootNode.reasoning}</p>
          </motion.div>
        )}

        {/* Supervisor Node */}
        {supervisorNode && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="amoled-card rounded-3xl p-6 border border-emerald-500/40 ml-4 lg:ml-8 relative">
            <div className="flex items-center justify-between mb-3">
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-xs font-mono font-bold uppercase">
                Supervisor Consensus
              </span>
              <span className="text-xs font-mono text-emerald-400 font-bold">Confidence: {(supervisorNode.confidence * 100).toFixed(0)}%</span>
            </div>
            <h3 className="text-lg font-extrabold text-white mb-1">{supervisorNode.title}</h3>
            <p className="text-xs text-slate-300 font-medium leading-relaxed">"{supervisorNode.reasoning}"</p>
          </motion.div>
        )}

        {/* Specialist Agent Children Nodes */}
        <div className="ml-8 lg:ml-16 grid grid-cols-1 md:grid-cols-2 gap-4">
          {agentNodes.map((agent, idx) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + (idx * 0.05) }}
              className="amoled-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-extrabold text-emerald-400 uppercase tracking-wider">{agent.title}</span>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                  {(agent.confidence * 100).toFixed(0)}% Conf
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed mb-3">"{agent.reasoning}"</p>
              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span>Recommendation:</span>
                <span className="text-white font-bold">{agent.recommendation}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Conflict Resolution Section */}
      {conflicts.length > 0 && (
        <div className="amoled-card rounded-3xl p-6 border border-rose-500/30">
          <h3 className="text-base font-extrabold text-white mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-rose-400" />
            <span>Agent Conflicts & Priority Resolution</span>
          </h3>

          <div className="space-y-3">
            {conflicts.map((c) => (
              <div key={c.conflict_id} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-xs space-y-2">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="font-bold text-emerald-400">Proposer: {c.proposing_agent}</span>
                  <span className="font-bold text-rose-400">Opposer: {c.opposing_agent}</span>
                </div>
                <p className="text-slate-400"><strong>Proposal:</strong> {c.proposal}</p>
                <p className="text-slate-400"><strong>Objection:</strong> {c.objection_reason}</p>
                <div className="pt-2 border-t border-slate-800 text-emerald-300 font-bold">
                  <strong>Supervisor Resolution:</strong> {c.supervisor_resolution}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
