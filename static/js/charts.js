/* =============================================================
   SPIDER — charts.js
   Chart.js configurations for all dashboard charts
   ============================================================= */

// ── Global Chart Defaults ──
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#6b7a99';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.padding = 16;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(17,24,39,0.95)';
  Chart.defaults.plugins.tooltip.borderColor = 'rgba(0,217,255,0.2)';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.titleColor = '#e8edf5';
  Chart.defaults.plugins.tooltip.bodyColor = '#6b7a99';
  Chart.defaults.scale.grid.color = 'rgba(255,255,255,0.04)';
  Chart.defaults.scale.border.color = 'rgba(255,255,255,0.06)';
}

const SpiderCharts = {
  charts: {},

  /* ── Gradient Helper ── */
  gradient(ctx, colors, vertical = true) {
    const g = vertical
      ? ctx.createLinearGradient(0, 0, 0, 300)
      : ctx.createLinearGradient(0, 0, 300, 0);
    colors.forEach(([stop, color]) => g.addColorStop(stop, color));
    return g;
  },

  /* ── Attack Timeline (line) ── */
  initAttackTimeline(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const c = ctx.getContext('2d');
    const gradFailed = this.gradient(c, [[0,'rgba(255,34,68,0.4)'], [1,'rgba(255,34,68,0)']]);
    const gradSuccess = this.gradient(c, [[0,'rgba(0,255,136,0.3)'], [1,'rgba(0,255,136,0)']]);

    if (this.charts[canvasId]) this.charts[canvasId].destroy();
    this.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(d => d.hour || d.date || d.week || ''),
        datasets: [
          {
            label: 'Failed',
            data: data.map(d => d.failed || 0),
            borderColor: '#ff2244',
            backgroundColor: gradFailed,
            borderWidth: 2,
            pointRadius: 3,
            pointBackgroundColor: '#ff2244',
            fill: true,
            tension: 0.4
          },
          {
            label: 'Success',
            data: data.map(d => d.success || 0),
            borderColor: '#00ff88',
            backgroundColor: gradSuccess,
            borderWidth: 2,
            pointRadius: 3,
            pointBackgroundColor: '#00ff88',
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: true } },
        scales: {
          y: { beginAtZero: true, ticks: { color: '#6b7a99' } },
          x: { ticks: { color: '#6b7a99', maxTicksLimit: 12 } }
        }
      }
    });
    return this.charts[canvasId];
  },

  /* ── Country Doughnut ── */
  initCountryChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const colors = ['#00d9ff','#ff007f','#00ff88','#8a2be2','#ff6b00','#ffd700','#ff2244','#00ccff','#cc00ff','#00ff44'];
    if (this.charts[canvasId]) this.charts[canvasId].destroy();
    this.charts[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.map(d => d.country),
        datasets: [{
          data: data.map(d => d.count),
          backgroundColor: colors.slice(0, data.length).map(c => c + '33'),
          borderColor: colors.slice(0, data.length),
          borderWidth: 2,
          hoverBorderWidth: 3,
          hoverBackgroundColor: colors.slice(0, data.length).map(c => c + '66'),
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: { position: 'right', labels: { color: '#e8edf5', font: { size: 11 } } }
        }
      }
    });
    return this.charts[canvasId];
  },

  /* ── Username Bar Chart ── */
  initUsernameChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const c = ctx.getContext('2d');
    const gradBar = this.gradient(c, [[0,'rgba(138,43,226,0.8)'], [1,'rgba(0,217,255,0.4)']], false);
    if (this.charts[canvasId]) this.charts[canvasId].destroy();
    this.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(d => d.username),
        datasets: [{
          label: 'Attempts',
          data: data.map(d => d.count),
          backgroundColor: gradBar,
          borderColor: '#8a2be2',
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, ticks: { color: '#6b7a99' } },
          y: { ticks: { color: '#e8edf5', font: { family: "'JetBrains Mono',monospace", size: 11 } } }
        }
      }
    });
    return this.charts[canvasId];
  },

  /* ── System CPU/RAM Line ── */
  initSystemChart(canvasId, labels, cpuData, ramData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const c = ctx.getContext('2d');
    const gradCpu = this.gradient(c, [[0,'rgba(0,217,255,0.3)'], [1,'rgba(0,217,255,0)']]);
    const gradRam = this.gradient(c, [[0,'rgba(138,43,226,0.3)'], [1,'rgba(138,43,226,0)']]);
    if (this.charts[canvasId]) this.charts[canvasId].destroy();
    this.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'CPU %',
            data: cpuData,
            borderColor: '#00d9ff',
            backgroundColor: gradCpu,
            borderWidth: 2,
            pointRadius: 0,
            fill: true,
            tension: 0.4
          },
          {
            label: 'RAM %',
            data: ramData,
            borderColor: '#8a2be2',
            backgroundColor: gradRam,
            borderWidth: 2,
            pointRadius: 0,
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: true } },
        scales: {
          y: { min: 0, max: 100, ticks: { color: '#6b7a99', callback: v => v + '%' } },
          x: { ticks: { color: '#6b7a99', maxTicksLimit: 8 } }
        }
      }
    });
    return this.charts[canvasId];
  },

  /* ── Network Throughput ── */
  initNetworkChart(canvasId, labels, inData, outData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (this.charts[canvasId]) this.charts[canvasId].destroy();
    this.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'In (MB)',
            data: inData,
            borderColor: '#00ff88',
            borderWidth: 2,
            pointRadius: 0,
            fill: false,
            tension: 0.4
          },
          {
            label: 'Out (MB)',
            data: outData,
            borderColor: '#ff007f',
            borderWidth: 2,
            pointRadius: 0,
            fill: false,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: { legend: { display: true } },
        scales: {
          y: { beginAtZero: true, ticks: { color: '#6b7a99' } },
          x: { ticks: { color: '#6b7a99', maxTicksLimit: 8 } }
        }
      }
    });
    return this.charts[canvasId];
  },

  /* ── Daily Bar Chart ── */
  initDailyChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (this.charts[canvasId]) this.charts[canvasId].destroy();
    this.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(d => d.date || ''),
        datasets: [{
          label: 'Total Attacks',
          data: data.map(d => d.total),
          backgroundColor: 'rgba(0,217,255,0.2)',
          borderColor: '#00d9ff',
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { color: '#6b7a99' } },
          x: { ticks: { color: '#6b7a99', maxTicksLimit: 10 } }
        }
      }
    });
    return this.charts[canvasId];
  },

  /* ── Event Type Pie ── */
  initEventTypePie(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const colors = ['#ff2244','#00d9ff','#8a2be2','#ff6b00','#00ff88','#ffd700'];
    const labels = {
      login_failed: 'Failed Login', login_success: 'Success',
      brute_force: 'Brute Force', root_login: 'Root Login',
      invalid_user: 'Invalid User', port_scan: 'Port Scan'
    };
    if (this.charts[canvasId]) this.charts[canvasId].destroy();
    this.charts[canvasId] = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: data.map(d => labels[d.event_type] || d.event_type),
        datasets: [{
          data: data.map(d => d.count),
          backgroundColor: colors.map(c => c + '44'),
          borderColor: colors,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#e8edf5', font: { size: 11 } } }
        }
      }
    });
    return this.charts[canvasId];
  },

  /* ── Update system chart live ── */
  updateSystemChart(chartId, labels, cpuData, ramData) {
    const chart = this.charts[chartId];
    if (!chart) return;
    chart.data.labels = labels;
    chart.data.datasets[0].data = cpuData;
    chart.data.datasets[1].data = ramData;
    chart.update('none');
  }
};

window.SpiderCharts = SpiderCharts;
