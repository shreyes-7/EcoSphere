/**
 * EcoSphere AI Building Energy Management System - Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initCharts();
  loadDashboardData();
  bindFormEvents();
});

// Navigation Handling
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const target = item.getAttribute('data-target');
      switchView(target);
    });
  });
}

function switchView(targetId) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.page-view').forEach(el => el.classList.remove('active'));

  const navEl = document.querySelector(`.nav-item[data-target="${targetId}"]`);
  const viewEl = document.getElementById(`view-${targetId}`);

  if (navEl) navEl.classList.add('active');
  if (viewEl) viewEl.classList.add('active');

  if (targetId === 'overview') loadDashboardData();
  if (targetId === 'history') fetchHistory();
  if (targetId === 'optimization') loadOptimizationAgentMatrix();
}

// Chart Instances
let overviewChart = null;
let compareChart = null;

function initCharts() {
  const ctxOverview = document.getElementById('overview-chart').getContext('2d');
  overviewChart = new Chart(ctxOverview, {
    type: 'line',
    data: {
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [
        {
          label: 'Electricity (kWh)',
          data: [20, 18, 45, 65, 58, 40, 22],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Cooling (kWh)',
          data: [10, 8, 25, 40, 35, 20, 12],
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.05)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Heating (kWh)',
          data: [15, 18, 10, 5, 8, 14, 16],
          borderColor: '#f59e0b',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } }
      },
      scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
      }
    }
  });

  const ctxCompare = document.getElementById('compare-chart').getContext('2d');
  compareChart = new Chart(ctxCompare, {
    type: 'bar',
    data: {
      labels: ['Total Energy', 'Electricity', 'Cooling', 'Heating', 'HVAC'],
      datasets: [
        {
          label: 'Baseline Run (kWh)',
          data: [200, 160, 70, 40, 50],
          backgroundColor: 'rgba(244, 63, 94, 0.7)',
          borderRadius: 6
        },
        {
          label: 'Optimized Run (kWh)',
          data: [168, 134, 58, 33, 41],
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } }
      },
      scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
      }
    }
  });
}

// API Loaders
async function loadDashboardData() {
  try {
    const res = await fetch('/dashboard/summary');
    if (!res.ok) throw new Error('Failed to load dashboard summary');
    const data = await res.json();

    document.getElementById('kpi-total-sims').innerText = data.total_simulations;
    document.getElementById('kpi-closed-loops').innerText = data.total_closed_loop_runs;
    document.getElementById('kpi-saved-kwh').innerText = `${data.total_energy_saved_kwh.toFixed(1)} kWh`;
    document.getElementById('kpi-avg-savings').innerText = `Avg ${data.average_savings_percent.toFixed(1)}% Reduction`;
    document.getElementById('kpi-agents').innerText = data.active_agents;

    loadAgentOverview();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function loadAgentOverview() {
  try {
    const res = await fetch('/agents/latest');
    if (!res.ok) return;
    const data = await res.json();

    if (data.supervisor_plan) {
      document.getElementById('supervisor-rec-text').innerText = 
        `"${data.supervisor_plan.final_recommendation}" (Confidence: ${Math.round(data.supervisor_plan.confidence * 100)}%)`;
    }

    const container = document.getElementById('overview-agent-cards');
    container.innerHTML = data.agents.map(agent => `
      <div class="agent-card">
        <div class="agent-card-header">
          <span class="agent-name">${getAgentIcon(agent.agent)} ${capitalize(agent.agent)} Agent</span>
          <span class="priority-badge priority-${agent.priority}">${agent.priority}</span>
        </div>
        <div class="agent-rec-text">${agent.recommendation}</div>
        <div class="confidence-bar-bg">
          <div class="confidence-bar-fill" style="width: ${Math.round(agent.confidence * 100)}%;"></div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Agent load failed:', err);
  }
}

async function loadOptimizationAgentMatrix() {
  try {
    const res = await fetch('/agents/latest');
    if (!res.ok) return;
    const data = await res.json();

    if (data.simulation_id) {
      const optSimInput = document.getElementById('opt-sim-id');
      if (optSimInput) optSimInput.value = data.simulation_id;
    }

    const container = document.getElementById('opt-agent-matrix');
    container.innerHTML = data.agents.map(agent => `
      <div class="agent-card">
        <div class="agent-card-header">
          <span class="agent-name">${getAgentIcon(agent.agent)} ${capitalize(agent.agent)} Agent</span>
          <span class="priority-badge priority-${agent.priority}">${agent.priority}</span>
        </div>
        <div class="agent-rec-text"><strong>Recommendation:</strong> ${agent.recommendation}</div>
        <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
          <strong>Explanation:</strong> ${agent.explanation}
        </div>
        <div style="font-size: 0.8rem; color: var(--primary-emerald);">
          Savings Impact: ~${agent.expected_savings}%
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Opt agent matrix load failed:', err);
  }
}

// Bind Forms & Button Events
function bindFormEvents() {
  // Simulation Form
  document.getElementById('sim-run-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-run-sim');
    btn.disabled = true;
    btn.innerHTML = '<span>⏳ Executing Simulation...</span>';

    try {
      const payload = {
        building_name: document.getElementById('sim-building-name').value,
        idf_file: document.getElementById('sim-idf-file').value,
        weather_file: document.getElementById('sim-weather-file').value,
      };

      const res = await fetch('/simulation/run-path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Simulation execution failed');
      }

      const sim = await res.json();
      showToast(`Simulation #${sim.id} completed successfully!`, 'success');
      
      document.getElementById('sim-result-box').innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.5rem;">
          <div class="agent-card">
            <div class="kpi-title">Electricity</div>
            <div class="kpi-value" style="font-size: 1.4rem;">${sim.electricity || sim.total_energy} kWh</div>
          </div>
          <div class="agent-card">
            <div class="kpi-title">Cooling Energy</div>
            <div class="kpi-value" style="font-size: 1.4rem;">${sim.cooling || 0} kWh</div>
          </div>
          <div class="agent-card">
            <div class="kpi-title">Heating Energy</div>
            <div class="kpi-value" style="font-size: 1.4rem;">${sim.heating || 0} kWh</div>
          </div>
          <div class="agent-card">
            <div class="kpi-title">HVAC Energy</div>
            <div class="kpi-value" style="font-size: 1.4rem;">${sim.hvac || 0} kWh</div>
          </div>
        </div>
      `;
      loadDashboardData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span>⚡ Run EnergyPlus Simulation</span>';
    }
  });

  // Closed Loop Optimization Form
  document.getElementById('opt-start-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-start-closed-loop');
    btn.disabled = true;
    btn.innerHTML = '<span>🚀 Optimizing Building...</span>';

    try {
      const payload = {
        simulation_id: parseInt(document.getElementById('opt-sim-id').value),
        max_iterations: parseInt(document.getElementById('opt-max-iter').value),
        target_reduction_percent: parseFloat(document.getElementById('opt-target-reduction').value),
        min_improvement_threshold_percent: 0.5
      };

      const res = await fetch('/optimize/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Closed-loop optimization failed');
      }

      const result = await res.json();
      window.latestClosedLoopRunId = result.closed_loop_run_id;
      showToast(`Closed Loop #${result.closed_loop_run_id} finished! Saved ${result.total_energy_saved_percent}%`, 'success');

      const card = document.getElementById('closed-loop-results-card');
      card.style.display = 'block';

      document.getElementById('closed-loop-breakdown').innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <div>
            <strong>Status:</strong> ${result.status} | 
            <strong>Iterations:</strong> ${result.total_iterations} | 
            <strong>Baseline:</strong> ${result.baseline_energy} kWh → 
            <strong>Final:</strong> ${result.final_energy} kWh | 
            <strong>Stop Reason:</strong> <span style="color: var(--primary-emerald);">${result.stop_reason}</span>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-secondary" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;" onclick="downloadReport('csv')">📥 CSV</button>
            <button class="btn btn-secondary" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;" onclick="downloadReport('json')">📥 JSON</button>
          </div>
        </div>
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>Iter</th>
                <th>Energy Before</th>
                <th>Energy After</th>
                <th>Iteration Saved (%)</th>
                <th>Cumulative Saved (%)</th>
                <th>Action Recommendation</th>
              </tr>
            </thead>
            <tbody>
              ${result.iterations.map(item => `
                <tr>
                  <td>${item.iteration}</td>
                  <td>${item.energy_before} kWh</td>
                  <td>${item.energy_after} kWh</td>
                  <td>${item.actual_savings}%</td>
                  <td>${item.cumulative_savings}%</td>
                  <td>${item.recommendation}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
      loadDashboardData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span>🚀 Execute Autonomous Closed Loop</span>';
    }
  });

  // Compare Runs Button
  document.getElementById('btn-compare-runs').addEventListener('click', async () => {
    const sim1 = document.getElementById('cmp-sim-1').value;
    const sim2 = document.getElementById('cmp-sim-2').value;

    try {
      const res = await fetch(`/optimize/compare?simulation_id_1=${sim1}&simulation_id_2=${sim2}`);
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to compare simulation runs');
      }

      const data = await res.json();
      updateCompareChart(data);

      document.getElementById('compare-metrics-box').innerHTML = `
        <div class="kpi-card" style="margin-bottom: 1rem;">
          <div class="kpi-title">Absolute Energy Saved</div>
          <div class="kpi-value">${data.energy_saved} kWh</div>
          <div class="kpi-sub">${data.savings_percent}% Total Reduction</div>
        </div>
        <div style="font-size: 0.9rem;">
          <p><strong>Baseline Building:</strong> ${data.simulation_1.building_name} (${data.simulation_1.electricity || data.simulation_1.total_energy} kWh)</p>
          <p><strong>Optimized Building:</strong> ${data.simulation_2.building_name} (${data.simulation_2.electricity || data.simulation_2.total_energy} kWh)</p>
        </div>
      `;
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Refresh History
  document.getElementById('btn-refresh-history').addEventListener('click', fetchHistory);

  // Modal Close
  document.getElementById('modal-close-btn').addEventListener('click', () => {
    document.getElementById('modal-explain').classList.remove('active');
  });
}

function updateCompareChart(data) {
  if (!compareChart) return;
  const s1 = data.simulation_1;
  const s2 = data.simulation_2;

  compareChart.data.datasets[0].data = [
    s1.total_energy || 0,
    s1.electricity || 0,
    s1.cooling || 0,
    s1.heating || 0,
    s1.hvac || 0
  ];
  compareChart.data.datasets[1].data = [
    s2.total_energy || 0,
    s2.electricity || 0,
    s2.cooling || 0,
    s2.heating || 0,
    s2.hvac || 0
  ];
  compareChart.update();
}

async function fetchHistory() {
  try {
    const res = await fetch('/optimize/history?limit=20');
    if (!res.ok) throw new Error('Failed to load history');
    const data = await res.json();

    const tbody = document.getElementById('history-table-body');
    if (data.history.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No optimization records found. Run a closed-loop session first.</td></tr>';
      return;
    }

    tbody.innerHTML = data.history.map(item => `
      <tr>
        <td>#${item.id}</td>
        <td>Sim #${item.simulation_id}</td>
        <td>Iter ${item.iteration}</td>
        <td>${item.energy_before || '-'}</td>
        <td>${item.energy_after || '-'}</td>
        <td><strong style="color: var(--primary-emerald);">${item.actual_savings || 0}%</strong></td>
        <td>${item.final_recommendation || '-'}</td>
        <td>
          <button class="btn btn-secondary" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;" onclick="showExplainabilityModal(${item.id})">
            🔍 AI Report
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function showExplainabilityModal(optId) {
  try {
    const res = await fetch(`/optimize/explanation/${optId}`);
    if (!res.ok) throw new Error('Failed to load explanation report');
    const exp = await res.json();

    const reportId = exp.optimization_id || exp.history_id || optId;
    const recText = exp.recommendation || exp.final_recommendation || 'Recommendation approved';
    const reasonText = exp.reason || exp.supervisor_explanation || 'Consensus recommendation reached across all specialist agents.';

    document.getElementById('modal-title').innerText = `Explainable AI Report (Optimization #${reportId})`;
    document.getElementById('modal-subtitle').innerText = exp.timestamp ? `Generated at ${new Date(exp.timestamp).toLocaleString()}` : 'Latest Real-Time Report';

    document.getElementById('modal-content').innerHTML = `
      <div class="card" style="margin-bottom: 1rem; background: rgba(15, 23, 42, 0.8);">
        <div style="font-size: 1.1rem; font-weight: 700; color: var(--primary-emerald); margin-bottom: 0.5rem;">
          Final Consensus Recommendation
        </div>
        <div>${recText}</div>
      </div>

      <div class="grid-2" style="margin-bottom: 1rem;">
        <div class="agent-card">
          <div class="kpi-title">Confidence Score</div>
          <div class="kpi-value" style="font-size: 1.5rem;">${Math.round((exp.confidence || 0) * 100)}%</div>
        </div>
        <div class="agent-card">
          <div class="kpi-title">Expected Savings</div>
          <div class="kpi-value" style="font-size: 1.5rem; color: var(--primary-emerald);">${exp.expected_savings || 0}%</div>
        </div>
      </div>

      <div class="card" style="margin-bottom: 1rem; background: rgba(15, 23, 42, 0.8);">
        <div class="card-title" style="margin-bottom: 0.5rem;">Decision Explanation</div>
        <p class="agent-rec-text">${reasonText}</p>
      </div>

      <div class="grid-2">
        <div class="agent-card">
          <div class="kpi-title">Comfort Impact Rule</div>
          <div style="font-size: 0.85rem; color: var(--text-main); margin-top: 0.3rem;">${exp.comfort_impact || 'Comfort preserved.'}</div>
        </div>
        <div class="agent-card">
          <div class="kpi-title">Carbon Impact Rule</div>
          <div style="font-size: 0.85rem; color: var(--text-main); margin-top: 0.3rem;">${exp.carbon_impact || 'Carbon emissions reduced.'}</div>
        </div>
      </div>
    `;

    document.getElementById('modal-explain').classList.add('active');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Helpers
function getAgentIcon(name) {
  const icons = { energy: '⚡', comfort: '🌡️', cost: '💰', sustainability: '🌱', supervisor: '🛡️' };
  return icons[name.toLowerCase()] || '🤖';
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  if (type === 'error') toast.style.borderColor = 'var(--accent-rose)';
  toast.innerText = message;

  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function downloadReport(format) {
  const runId = window.latestClosedLoopRunId || 1;
  const url = `/analytics/export/${format}/${runId}`;
  window.open(url, '_blank');
  showToast(`Downloading ${format.toUpperCase()} report for Run #${runId}...`, 'info');
}
