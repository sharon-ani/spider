/* =============================================================
   SPIDER — realtime.js
   SSE stream + polling for live attack feed
   ============================================================= */

const RealtimeFeed = {
  maxRows: 50,
  feedTable: null,
  sseSource: null,

  init(feedTableId) {
    this.feedTable = document.getElementById(feedTableId);
    this.startSSE();
    // Update stats every 5 seconds
    this.pollStats();
    setInterval(() => this.pollStats(), 5000);
  },

  startSSE() {
    if (typeof EventSource === 'undefined') {
      this.startPolling();
      return;
    }
    try {
      this.sseSource = new EventSource('/api/stream');
      this.sseSource.onmessage = (e) => {
        try {
          const attack = JSON.parse(e.data);
          this.injectFeedRow(attack);
          this.showAlertToast(attack);
        } catch(err) {}
      };
      this.sseSource.onerror = () => {
        this.sseSource.close();
        setTimeout(() => this.startSSE(), 8000);
      };
    } catch(e) {
      this.startPolling();
    }
  },

  startPolling() {
    let lastId = 0;
    const poll = async () => {
      const data = await SPIDER.fetchJSON('/api/attacks/latest?limit=5');
      if (!data) return;
      data.forEach(a => {
        if (a.id > lastId) {
          lastId = a.id;
          this.injectFeedRow(a);
        }
      });
      if (data.length > 0) lastId = Math.max(...data.map(a => a.id));
    };
    setInterval(poll, 5000);
  },

  injectFeedRow(attack) {
    if (!this.feedTable) return;
    const tbody = this.feedTable.querySelector('tbody') || this.feedTable;
    const row = document.createElement('tr');
    row.className = 'feed-row-new';
    row.innerHTML = `
      <td class="font-mono fs-12" style="color:var(--muted)">${attack.timestamp || '—'}</td>
      <td><span class="ip-badge">${attack.ip}</span></td>
      <td>${SPIDER.flagEmoji(attack.country_code)} ${attack.country || '—'}</td>
      <td style="color:var(--white)">${attack.username}</td>
      <td>${SPIDER.statusBadge(attack.status)}</td>
      <td>${SPIDER.eventBadge(attack.event_type)}</td>
    `;
    tbody.insertBefore(row, tbody.firstChild);

    // Remove old rows if over limit
    const rows = tbody.querySelectorAll('tr');
    if (rows.length > this.maxRows) {
      for (let i = this.maxRows; i < rows.length; i++) rows[i].remove();
    }
  },

  showAlertToast(attack) {
    if (attack.is_brute_force) {
      SPIDER.toast('🚨 Brute Force Attack',
        `${attack.country || 'Unknown'} — ${attack.ip} targeting <b>${attack.username}</b>`,
        'critical', 8000);
    } else if (attack.is_root && attack.status === 'success') {
      SPIDER.toast('🔴 Root Login Success!',
        `${attack.ip} (${attack.country || 'Unknown'}) logged in as root!`,
        'critical', 10000);
    } else if (attack.is_root) {
      SPIDER.toast('⚠️ Root Login Attempt',
        `${attack.ip} from ${attack.country || 'Unknown'}`,
        'warning', 6000);
    } else if (attack.status === 'success') {
      SPIDER.toast('✅ Login Success',
        `${attack.username}@${attack.ip} from ${attack.country || 'Unknown'}`,
        'success', 4000);
    }
  },

  async pollStats() {
    const data = await SPIDER.fetchJSON('/api/stats');
    if (!data) return;

    const updateEl = (id, val) => {
      const el = document.getElementById(id);
      if (el && el.textContent !== String(val)) {
        const old = parseInt(el.textContent.replace(/,/g,'')) || 0;
        SPIDER.animateCounter(el, typeof val === 'number' ? val : parseInt(val) || 0);
      }
    };

    updateEl('statTotal',   data.total_attempts);
    updateEl('statFailed',  data.failed_logins);
    updateEl('statSuccess', data.success_logins);
    updateEl('statSessions',data.active_sessions);
    updateEl('statThreats', data.active_threats);
    updateEl('statBrute',   data.brute_force_attacks);

    // System stats
    if (data.system) {
      this.updateSystemStats(data.system);
    }

    // Last updated
    const ts = document.getElementById('lastUpdated');
    if (ts) ts.textContent = 'Updated ' + SPIDER.timeAgo(data.timestamp);
  },

  updateSystemStats(sys) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    const setWidth = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.style.width = Math.min(100, val) + '%';
    };

    set('sysCpu',  sys.cpu_percent + '%');
    set('sysRam',  sys.ram_percent + '%');
    set('sysDisk', sys.disk_percent + '%');
    set('sysUptime', sys.uptime_str);

    setWidth('cpuBar',  sys.cpu_percent);
    setWidth('ramBar',  sys.ram_percent);
    setWidth('diskBar', sys.disk_percent);

    // Color bars by threshold
    const colorBar = (id, val) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.className = 'progress-fill ' + (val > 85 ? 'red' : val > 65 ? 'orange' : 'green');
    };
    colorBar('cpuBar',  sys.cpu_percent);
    colorBar('ramBar',  sys.ram_percent);
    colorBar('diskBar', sys.disk_percent);
  }
};

window.RealtimeFeed = RealtimeFeed;
