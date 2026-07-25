import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { PlayCircle, Building2, FileCode, CloudSun, CheckCircle2, Zap, Activity, Loader2, UploadCloud } from 'lucide-react';

export default function SimulationRunner({ onSimulationCreated, setToast }) {
  const [buildingName, setBuildingName] = useState('Commercial Test Facility');
  const [idfFile, setIdfFile] = useState('energyplus/building.idf');
  const [weatherFile, setWeatherFile] = useState('weather/weather.epw');
  const [runnerMode, setRunnerMode] = useState('preset'); // 'preset' or 'upload'
  const [uploadedIdf, setUploadedIdf] = useState(null);
  const [uploadedEpw, setUploadedEpw] = useState(null);
  const [loading, setLoading] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);
  const [error, setError] = useState(null);

  const PRESETS = [
    { name: 'Commercial Test Facility', idf: 'energyplus/building.idf', epw: 'weather/weather.epw' },
    { name: 'Small Office Sandbox', idf: 'energyplus/small_office.idf', epw: 'weather/weather.epw' },
    { name: 'Retail Store Facility', idf: 'energyplus/retail.idf', epw: 'weather/weather.epw' },
  ];

  const handleApplyPreset = (preset) => {
    setBuildingName(preset.name);
    setIdfFile(preset.idf);
    setWeatherFile(preset.epw);
  };

  const handleRunSimulation = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    if (setToast) setToast({ type: 'loading', title: 'Running Building Simulation', message: 'Executing EnergyPlus physics engine...' });

    try {
      let res;
      if (runnerMode === 'upload') {
        if (!uploadedIdf || !uploadedEpw) {
          throw new Error('Please select both an .idf building file and an .epw weather file to upload');
        }
        const formData = new FormData();
        formData.append('building_name', buildingName);
        formData.append('idf_file', uploadedIdf);
        formData.append('weather_file', uploadedEpw);

        res = await fetch('/simulation/run', {
          method: 'POST',
          body: formData,
        });
      } else {
        res = await fetch('/simulation/run-path', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            building_name: buildingName,
            idf_file: idfFile,
            weather_file: weatherFile,
          }),
        });
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Simulation failed: ${res.statusText}`);
      }

      const data = await res.json();
      setSimulationResult(data);
      if (onSimulationCreated) onSimulationCreated(data);
      if (setToast) setToast({ type: 'success', title: 'Simulation Complete', message: `Simulation #${data.id} completed: ${data.electricity} kWh` });
    } catch (err) {
      setError(err.message || 'Error executing simulation');
      if (setToast) setToast({ type: 'error', title: 'Simulation Failed', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Presets & Mode Selector Row */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-xl p-1 shadow-inner">
          <button
            onClick={() => setRunnerMode('preset')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
              runnerMode === 'preset' ? 'bg-emerald-500 text-slate-950 shadow-md font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            Server Path / Presets
          </button>
          <button
            onClick={() => setRunnerMode('upload')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
              runnerMode === 'upload' ? 'bg-emerald-500 text-slate-950 shadow-md font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            Upload Local Files (.idf & .epw)
          </button>
        </div>

        {runnerMode === 'preset' && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Presets:</span>
            {PRESETS.map((p, idx) => (
              <motion.button
                key={idx}
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                onClick={() => handleApplyPreset(p)}
                className="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 hover:border-emerald-500/40 hover:text-emerald-400 transition"
              >
                {p.name}
              </motion.button>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Form (7 cols) */}
        <motion.div
          initial={{ opacity: 0, x: -15 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-7 glass-panel rounded-3xl p-6 border border-slate-800"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                {runnerMode === 'upload' ? 'Upload Local Building Model' : 'Configure Path Building Simulation'}
              </h3>
              <p className="text-xs text-slate-400">
                {runnerMode === 'upload' ? 'Upload custom .idf geometry and .epw weather files from your PC' : 'Specify on-disk building geometry IDF and weather file paths'}
              </p>
            </div>
          </div>

          <form onSubmit={handleRunSimulation} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Building Facility Name</label>
              <input
                type="text"
                value={buildingName}
                onChange={(e) => setBuildingName(e.target.value)}
                required
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-emerald-500 transition"
              />
            </div>

            {runnerMode === 'preset' ? (
              <>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <FileCode className="w-4 h-4 text-emerald-400" /> Building Geometry File Path (.idf)
                  </label>
                  <input
                    type="text"
                    value={idfFile}
                    onChange={(e) => setIdfFile(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white font-mono focus:outline-none focus:border-emerald-500 transition"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <CloudSun className="w-4 h-4 text-cyan-400" /> EPW Weather Data File Path (.epw)
                  </label>
                  <input
                    type="text"
                    value={weatherFile}
                    onChange={(e) => setWeatherFile(e.target.value)}
                    required
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white font-mono focus:outline-none focus:border-emerald-500 transition"
                  />
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <FileCode className="w-4 h-4 text-emerald-400" /> Select Building Geometry File (.idf)
                  </label>
                  <input
                    type="file"
                    accept=".idf"
                    onChange={(e) => setUploadedIdf(e.target.files[0])}
                    required
                    className="w-full px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 file:mr-4 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-500 file:text-slate-950 hover:file:bg-emerald-400"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <CloudSun className="w-4 h-4 text-cyan-400" /> Select EPW Weather File (.epw)
                  </label>
                  <input
                    type="file"
                    accept=".epw"
                    onChange={(e) => setUploadedEpw(e.target.files[0])}
                    required
                    className="w-full px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 file:mr-4 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-cyan-500 file:text-slate-950 hover:file:bg-cyan-400"
                  />
                </div>
              </>
            )}

            {error && (
              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400">
                {error}
              </div>
            )}

            <motion.button
              whileHover={{ scale: loading ? 1 : 1.02 }}
              whileTap={{ scale: loading ? 1 : 0.97 }}
              type="submit"
              disabled={loading}
              className={`w-full mt-3 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2.5 transition-all shadow-lg ${
                loading
                  ? 'bg-slate-800 text-emerald-400 border border-emerald-500/40 cursor-wait'
                  : 'bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-slate-950 hover:from-emerald-400 hover:to-cyan-400 shadow-emerald-500/20'
              }`}
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin text-emerald-400" />
                  <span className="font-mono text-emerald-300 animate-pulse">Running EnergyPlus Engine...</span>
                </>
              ) : (
                <>
                  <PlayCircle className="w-5 h-5 fill-current" />
                  <span>Run EnergyPlus Simulation</span>
                </>
              )}
            </motion.button>
          </form>
        </motion.div>

        {/* Simulation Output Result Card (5 cols) */}
        <motion.div
          initial={{ opacity: 0, x: 15 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-5 glass-panel rounded-3xl p-6 border border-slate-800 flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Latest Simulation Output
              </span>
              {simulationResult && (
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-[11px] font-mono font-semibold">
                  Sim #{simulationResult.id}
                </span>
              )}
            </div>

            {loading ? (
              <div className="text-center py-16">
                <Loader2 className="w-10 h-10 text-emerald-400 mx-auto mb-3 animate-spin" />
                <p className="text-sm font-bold text-white">Simulating Building Performance...</p>
                <p className="text-xs text-slate-400 mt-1">Extracting zone temperatures & kWh consumption</p>
              </div>
            ) : simulationResult ? (
              <div className="space-y-4">
                <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Facility Name</span>
                  <p className="text-base font-bold text-white mt-0.5">{simulationResult.building_name}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-800">
                    <span className="text-[11px] text-slate-400 block">Electricity</span>
                    <span className="text-lg font-bold text-emerald-400 font-mono">
                      {(simulationResult.electricity || 160.0).toFixed(1)} kWh
                    </span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-800">
                    <span className="text-[11px] text-slate-400 block">HVAC Load</span>
                    <span className="text-lg font-bold text-cyan-400 font-mono">
                      {(simulationResult.hvac || 50.0).toFixed(1)} kWh
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-[11px] text-slate-400 truncate">
                  Output: {simulationResult.output_folder}
                </div>
              </div>
            ) : (
              <div className="text-center py-16">
                <Activity className="w-12 h-12 text-slate-700 mx-auto mb-3 animate-pulse" />
                <p className="text-sm font-medium text-slate-400">No simulation executed yet.</p>
                <p className="text-xs text-slate-400 mt-1">Fill the form and click "Run EnergyPlus Simulation".</p>
              </div>
            )}
          </div>

          {simulationResult && (
            <div className="pt-4 border-t border-slate-800 flex justify-between items-center text-xs text-slate-400 font-mono">
              <span>Status: {simulationResult.status}</span>
              <span className="text-emerald-400 font-semibold">Ready for Closed Loop</span>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
