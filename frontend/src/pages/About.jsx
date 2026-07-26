import React from 'react';
import { motion } from 'framer-motion';
import { 
  Leaf, 
  Sparkles, 
  Cpu, 
  Layers, 
  GitCommit, 
  PlayCircle, 
  ShieldCheck, 
  Activity, 
  History, 
  MessageSquare, 
  FileText, 
  Code2, 
  ExternalLink, 
  Github, 
  CheckCircle2, 
  ArrowRight,
  Server,
  Database,
  Terminal,
  Zap,
  Globe,
  Award
} from 'lucide-react';

export default function About({ onNavigate }) {
  const coreFeatures = [
    { title: 'AI Digital Twin', desc: 'Real-time 6-zone thermal physics mapping with 100% ASHRAE-55 PMV telemetry.', icon: Layers },
    { title: 'Interactive Building Heatmap', desc: 'Dynamic thermal and load balance spatial distribution rendering.', icon: Zap },
    { title: 'Multi-Agent Swarm Intelligence', desc: 'Specialized Energy, Comfort, Cost, and Sustainability AI agents.', icon: Cpu },
    { title: 'Supervisor Consensus Engine', desc: 'Conflict resolution matrix enforcing strict comfort guardrails.', icon: ShieldCheck },
    { title: 'Reinforcement Learning Optimization', desc: 'Continuous q-policy learning for adaptive HVAC setpoint tuning.', icon: Activity },
    { title: 'Explainable AI Decision Tree', desc: 'Hierarchical node graph explaining supervisor rationale.', icon: GitCommit },
    { title: 'Closed Loop Optimization', desc: 'Autonomous AST IDF modification and closed-loop validation.', icon: PlayCircle },
    { title: 'Self-Healing Building Intelligence', desc: 'Autonomous anomaly detection and automatic failover recovery.', icon: CheckCircle2 },
    { title: 'Optimization Playback', desc: 'Time-travel analytics reconstructing historical optimization frames.', icon: History },
    { title: 'AI Facility Manager', desc: 'Conversational FastMCP tool-calling assistant for natural queries.', icon: MessageSquare },
    { title: 'Historical Analytics', desc: 'Comprehensive side-by-side kWh and cost savings comparison.', icon: FileText },
    { title: 'EnergyPlus Physics Simulation', desc: 'U.S. DOE C++ physics engine for heat balance and load calculation.', icon: Server },
  ];

  const techStack = [
    { category: 'Frontend', items: ['React', 'JavaScript', 'TailwindCSS', 'Recharts'] },
    { category: 'Backend', items: ['FastAPI', 'Python', 'SQLAlchemy', 'SQLite', 'FastMCP'] },
    { category: 'Simulation', items: ['EnergyPlus C++ Engine', 'IDF AST Modifier', 'EPW Weather'] },
    { category: 'Optimization', items: ['Multi-Agent AI', 'Supervisor Agent', 'Reinforcement Learning', 'Explainable AI'] },
  ];

  const archNodes = [
    { title: 'User', icon: Terminal, color: 'text-emerald-400' },
    { title: 'FastAPI', icon: Server, color: 'text-cyan-400' },
    { title: 'EnergyPlus', icon: Zap, color: 'text-amber-400' },
    { title: 'Multi-Agent Swarm', icon: Cpu, color: 'text-purple-400' },
    { title: 'Supervisor', icon: ShieldCheck, color: 'text-emerald-400' },
    { title: 'Optimization Engine', icon: Activity, color: 'text-cyan-400' },
    { title: 'Closed Loop', icon: PlayCircle, color: 'text-amber-400' },
    { title: 'Digital Twin', icon: Layers, color: 'text-purple-400' },
    { title: 'Reports', icon: FileText, color: 'text-emerald-400' },
  ];

  const projectSpecs = [
    { label: 'Version', value: '1.0.0' },
    { label: 'Architecture', value: 'Production' },
    { label: 'License', value: 'MIT Open Source' },
    { label: 'Platform', value: 'Cross Platform (Win/Linux/macOS)' },
    { label: 'Simulation Engine', value: 'EnergyPlus' },
    { label: 'Optimization', value: 'Closed Loop Autonomous AI' },
  ];

  return (
    <div className="space-y-10">
      
      {/* 1. HERO SECTION */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-3xl p-8 sm:p-10 border border-emerald-500/30 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-emerald-500/10 via-cyan-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-4 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Physical AI Platform</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent tracking-tight">
            EcoSphere
          </h1>

          <p className="text-base text-slate-300 leading-relaxed font-sans font-normal">
            Production-ready AI platform for intelligent building optimization using EnergyPlus simulations, explainable multi-agent AI, reinforcement learning and closed-loop autonomous control.
          </p>
        </div>
      </motion.div>

      {/* 2. MISSION STATEMENT */}
      <div className="amoled-card rounded-3xl p-8 border border-slate-800 space-y-3">
        <h3 className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-2">
          <Globe className="w-4 h-4" /> Mission Statement
        </h3>
        <p className="text-base text-slate-200 leading-relaxed font-sans">
          EcoSphere transforms traditional building simulation into an autonomous AI-driven optimization platform capable of continuously improving energy efficiency, occupant comfort, operational cost and sustainability through real-time multi-agent reasoning and physics-based simulation.
        </p>
      </div>

      {/* 3. CORE FEATURES GRID */}
      <div className="space-y-4">
        <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Cpu className="w-4 h-4 text-emerald-400" /> Core Platform Capabilities
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {coreFeatures.map((feat) => {
            const Icon = feat.icon;
            return (
              <div key={feat.title} className="amoled-card rounded-2xl p-5 border border-slate-800 hover:border-emerald-500/40 transition group">
                <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-3 group-hover:scale-110 transition">
                  <Icon className="w-4 h-4" />
                </div>
                <h4 className="text-sm font-bold text-white mb-1">{feat.title}</h4>
                <p className="text-xs text-slate-400 leading-relaxed">{feat.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* 4. TECHNOLOGY STACK */}
      <div className="space-y-4">
        <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Code2 className="w-4 h-4 text-cyan-400" /> Technology Architecture
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {techStack.map((group) => (
            <div key={group.category} className="amoled-card rounded-2xl p-5 border border-slate-800 space-y-3">
              <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider block border-b border-slate-800 pb-2">
                {group.category}
              </span>
              <div className="space-y-1.5">
                {group.items.map((item) => (
                  <div key={item} className="flex items-center gap-2 text-xs font-mono text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. ARCHITECTURE DIAGRAM */}
      <div className="amoled-card rounded-3xl p-8 border border-slate-800 space-y-6">
        <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Layers className="w-4 h-4 text-purple-400" /> End-to-End System Pipeline Architecture
        </h3>

        <div className="flex flex-wrap items-center justify-center gap-3 py-4">
          {archNodes.map((node, index) => {
            const NodeIcon = node.icon;
            return (
              <React.Fragment key={node.title}>
                <div className="px-4 py-3 rounded-2xl bg-[#000000] border border-slate-800 flex items-center gap-2.5 shadow-lg">
                  <NodeIcon className={`w-4 h-4 ${node.color}`} />
                  <span className="text-xs font-mono font-bold text-white">{node.title}</span>
                </div>
                {index < archNodes.length - 1 && (
                  <ArrowRight className="w-4 h-4 text-slate-600 shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* 6. PROJECT SPECIFICATIONS & GITHUB */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project Info */}
        <div className="lg:col-span-2 amoled-card rounded-3xl p-6 border border-slate-800 space-y-4">
          <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Award className="w-4 h-4 text-amber-400" /> Project Specifications
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {projectSpecs.map((spec) => (
              <div key={spec.label} className="p-3 rounded-xl bg-[#000000] border border-slate-800">
                <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">{spec.label}</span>
                <span className="text-xs font-mono font-bold text-white mt-0.5 block">{spec.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* GitHub Repository Box */}
        <div className="amoled-card rounded-3xl p-6 border border-emerald-500/30 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-mono font-bold uppercase tracking-wider mb-2">
              <Github className="w-4 h-4" /> Open Source Codebase
            </div>
            <h4 className="text-lg font-extrabold text-white">Project Repository</h4>
            <p className="text-xs text-slate-400 mt-1">Explore source code, schemas, FastMCP agents, and tests.</p>
          </div>

          <a
            href="https://github.com/shreyes-7/EcoSphere"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-3 px-4 rounded-2xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-slate-950 font-extrabold text-xs flex items-center justify-center gap-2 hover:opacity-90 transition shadow-lg shadow-emerald-500/20"
          >
            <Github className="w-4 h-4" />
            <span>github.com/shreyes-7/EcoSphere</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* 7. CREDITS SECTION */}
      <div className="amoled-card rounded-3xl p-6 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono">
        <div>
          <span className="text-slate-500 uppercase tracking-wider block text-[10px]">Lead Software Engineer</span>
          <span className="text-sm font-extrabold text-white">Developed by Shreyes Jaiswal</span>
        </div>

      </div>
    </div>
  );
}
