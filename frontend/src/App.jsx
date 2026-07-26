import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Toast from './components/Toast';
import FacilityManagerChat from './components/FacilityManagerChat';
import Overview from './pages/Overview';
import DigitalTwinView from './pages/DigitalTwinView';
import DecisionTree from './pages/DecisionTree';
import SimulationRunner from './pages/SimulationRunner';
import Optimization from './pages/Optimization';
import Comparison from './pages/Comparison';
import History from './pages/History';
import Telemetry from './pages/Telemetry';
import About from './pages/About';
import Footer from './components/Footer';

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
    setTimeout(() => {
      setToastState((curr) => (curr?.id === id ? null : curr));
    }, 2000);
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
    setToast({ message: 'Launching multi-agent closed-loop optimization...', type: 'info' });
    try {
      const res = await fetch('/optimize/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulation_id: 1,
          max_iterations: 2,
          target_savings_percent: 10.0,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setSupervisorPlan(data);
        setToast({ message: 'Closed-loop optimization completed cleanly!', type: 'success' });
      } else {
        setToast({ message: 'Optimization execution failed', type: 'error' });
      }
    } catch (err) {
      console.error(err);
      setToast({ message: 'Failed to execute closed-loop run', type: 'error' });
    } finally {
      setIsExecutingClosedLoop(false);
    }
  };

  const handleRefresh = async () => {
    setToast({ message: 'Refreshed system telemetry & building state', type: 'info' });
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <Overview
            latestSimulation={latestSimulation}
            supervisorPlan={supervisorPlan}
            setToast={setToast}
            onNavigate={setActiveTab}
            onExecuteClosedLoop={handleExecuteClosedLoopGlobal}
          />
        );
      case 'digital-twin':
        return <DigitalTwinView setToast={setToast} />;
      case 'decision-tree':
        return <DecisionTree setToast={setToast} />;
      case 'simulation':
        return <SimulationRunner setLatestSimulation={setLatestSimulation} setToast={setToast} />;
      case 'optimization':
        return (
          <Optimization
            latestSimulation={latestSimulation}
            supervisorPlan={supervisorPlan}
            setSupervisorPlan={setSupervisorPlan}
            setToast={setToast}
          />
        );
      case 'comparison':
        return <Comparison setToast={setToast} />;
      case 'history':
        return <History setToast={setToast} />;
      case 'telemetry':
        return <Telemetry setToast={setToast} />;
      case 'about':
        return <About onNavigate={setActiveTab} />;
      default:
        return (
          <Overview
            latestSimulation={latestSimulation}
            supervisorPlan={supervisorPlan}
            setToast={setToast}
            onNavigate={setActiveTab}
            onExecuteClosedLoop={handleExecuteClosedLoopGlobal}
          />
        );
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#000000] amoled-grid-bg text-slate-100 overflow-hidden font-sans relative">
      {/* Toast Notification Container */}
      <Toast toast={toast} onClose={() => setToast(null)} />

      {/* Floating AI Facility Manager Chatbot Widget */}
      <FacilityManagerChat />

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
        <main className="flex-1 overflow-y-auto p-8 flex flex-col justify-between">
          <div className="w-full">
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
          </div>

          <Footer onNavigate={setActiveTab} />
        </main>
      </div>
    </div>
  );
}
