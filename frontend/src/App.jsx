import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Toast from './components/Toast';
import Overview from './pages/Overview';
import SimulationRunner from './pages/SimulationRunner';
import Optimization from './pages/Optimization';
import Comparison from './pages/Comparison';
import History from './pages/History';
import Telemetry from './pages/Telemetry';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [latestSimulation, setLatestSimulation] = useState(null);
  const [supervisorPlan, setSupervisorPlan] = useState(null);
  const [isExecutingClosedLoop, setIsExecutingClosedLoop] = useState(false);
  const [toast, setToastState] = useState(null);

  const setToast = (toastData) => {
    if (!toastData) {
      setToastState(null);
      return;
    }
    const id = Date.now();
    setToastState({ ...toastData, id });
    if (toastData.type !== 'loading') {
      setTimeout(() => {
        setToastState((curr) => (curr?.id === id ? null : curr));
      }, 4500);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const res = await fetch('/agents/latest');
      if (res.ok) {
        const data = await res.json();
        setSupervisorPlan(data.supervisor_plan);
      }

      const simRes = await fetch('/simulation/latest');
      if (simRes.ok) {
        const simData = await simRes.json();
        setLatestSimulation(simData);
      }
    } catch (err) {
      console.error('Error fetching initial dashboard data:', err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleExecuteClosedLoopGlobal = async () => {
    setIsExecutingClosedLoop(true);
    setActiveTab('optimization');
    setToast({ type: 'loading', title: 'Executing Autonomous Closed Loop', message: 'Gathering multi-agent evaluations...' });

    try {
      const res = await fetch('/optimize/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          max_iterations: 4,
          target_savings_percent: 15.0,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        await fetchDashboardData();
        setToast({ type: 'success', title: 'Closed Loop Success!', message: `Achieved ${data.actual_savings_percent}% reduction!` });
      } else {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Closed loop execution failed');
      }
    } catch (err) {
      console.error('Error executing closed loop:', err);
      setToast({ type: 'error', title: 'Execution Error', message: err.message });
    } finally {
      setIsExecutingClosedLoop(false);
    }
  };

  const handleRefresh = async () => {
    setToast({ type: 'loading', title: 'Refreshing System State', message: 'Fetching latest metrics & telemetry...' });
    await fetchDashboardData();
    setToast({ type: 'success', title: 'Dashboard Updated', message: 'Telemetry & metrics synchronized' });
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <Overview
            latestSimulation={latestSimulation}
            supervisorPlan={supervisorPlan}
            onNavigate={(tab) => setActiveTab(tab)}
            setToast={setToast}
          />
        );
      case 'simulation':
        return (
          <SimulationRunner
            onSimulationCreated={(simData) => {
              setLatestSimulation(simData);
              fetchDashboardData();
            }}
            setToast={setToast}
          />
        );
      case 'optimization':
        return (
          <Optimization
            latestSimulation={latestSimulation}
            onClosedLoopComplete={() => fetchDashboardData()}
            setToast={setToast}
          />
        );
      case 'comparison':
        return <Comparison setToast={setToast} />;
      case 'history':
        return <History setToast={setToast} />;
      case 'telemetry':
        return <Telemetry setToast={setToast} />;
      default:
        return <Overview latestSimulation={latestSimulation} supervisorPlan={supervisorPlan} setToast={setToast} />;
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#0b0f19] text-slate-100 overflow-hidden font-sans">
      {/* Toast Notification Container */}
      <Toast toast={toast} onClose={() => setToast(null)} />

      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <Header
          activeTab={activeTab}
          onRefresh={handleRefresh}
          onExecuteClosedLoop={handleExecuteClosedLoopGlobal}
          isExecuting={isExecutingClosedLoop}
        />

        {/* Dynamic Page Container with Framer Motion Page Transition */}
        <main className="flex-1 overflow-y-auto p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.18, ease: 'easeInOut' }}
              className="max-w-7xl mx-auto"
            >
              {renderActiveTab()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
