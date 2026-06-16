/* =============================================================
   SPIDER — main.js
   Core app: sidebar toggle, clock, toasts, utilities
   ============================================================= */

const SPIDER = {
  sidebarCollapsed: false,
  refreshInterval: 5000,

  init() {
    this.initSidebar();
    this.initClock();
    this.initToasts();
    this.initLoadingScreen();
    this.initParticles();
    this.highlightNavItem();
    this.initMatrixCanvas();
  },

  /* ── Sidebar ── */
  initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const topHeader = document.getElementById('topHeader');
    const toggleBtn = document.getElementById('sidebarToggle');

    if (!sidebar) return;

    const collapsed = localStorage.getItem('spider_sidebar') === 'collapsed';
    if (collapsed) this.collapseSidebar(sidebar, mainContent, topHeader);

    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        this.sidebarCollapsed = !this.sidebarCollapsed;
        if (this.sidebarCollapsed) {
          this.collapseSidebar(sidebar, mainContent, topHeader);
          localStorage.setItem('spider_sidebar', 'collapsed');
        } else {
          this.expandSidebar(sidebar, mainContent, topHeader);
          localStorage.setItem('spider_sidebar', 'expanded');
        }
      });
    }
  },

  collapseSidebar(sidebar, main, header) {
    this.sidebarCollapsed = true;
    sidebar?.classList.add('collapsed');
    main?.classList.add('sidebar-collapsed');
    header?.classList.add('sidebar-collapsed');
  },

  expandSidebar(sidebar, main, header) {
    this.sidebarCollapsed = false;
    sidebar?.classList.remove('collapsed');
    main?.classList.remove('sidebar-collapsed');
    header?.classList.remove('sidebar-collapsed');
  },

  highlightNavItem() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.remove('active');
      const href = el.getAttribute('href');
      if (href && (path === href || (href !== '/' && path.startsWith(href)))) {
        el.classList.add('active');
      }
    });
  },

  /* ── Clock ── */
  initClock() {
    const el = document.getElementById('headerClock');
    if (!el) return;
    const update = () => {
      const now = new Date();
      el.textContent = now.toLocaleTimeString('en-GB', {hour12: false}) +
                       ' ' + now.toLocaleDateString('en-GB');
    };
    update();
    setInterval(update, 1000);
  },

  /* ── Toast Notifications ── */
  initToasts() {
    this._toastContainer = document.getElementById('toastContainer');
    if (!this._toastContainer) {
      this._toastContainer = document.createElement('div');
      this._toastContainer.className = 'toast-container';
      this._toastContainer.id = 'toastContainer';
      document.body.appendChild(this._toastContainer);
    }
  },

  toast(title, message, type = 'info', duration = 5000) {
    const icons = {
      critical: 'fa-exclamation-triangle',
      warning:  'fa-exclamation-circle',
      success:  'fa-check-circle',
      info:     'fa-info-circle'
    };
    const t = document.createElement('div');
    t.className = `toast-cyber ${type}`;
    t.innerHTML = `
      <i class="fas ${icons[type] || icons.info} toast-icon"></i>
      <div>
        <div class="toast-title">${title}</div>
        <div class="toast-body">${message}</div>
      </div>
      <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--muted);cursor:pointer;margin-left:auto;padding:0 0 0 10px;font-size:14px;">&times;</button>
    `;
    this._toastContainer.appendChild(t);
    if (duration > 0) {
      setTimeout(() => {
        t.style.animation = 'fadeOutRight 0.3s ease forwards';
        setTimeout(() => t.remove(), 300);
      }, duration);
    }
    return t;
  },

  /* ── Loading Screen ── */
  initLoadingScreen() {
    const ls = document.getElementById('loadingScreen');
    if (!ls) return;
    setTimeout(() => {
      ls.style.opacity = '0';
      setTimeout(() => ls.remove(), 500);
    }, 1200);
  },

  /* ── Matrix Canvas ── */
  initMatrixCanvas() {
    const canvas = document.getElementById('matrixCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    });

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,.<>?';
    const cols = Math.floor(canvas.width / 16);
    const drops = Array(cols).fill(1);

    const draw = () => {
      ctx.fillStyle = 'rgba(10, 15, 26, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#00d9ff';
      ctx.font = '12px JetBrains Mono, monospace';

      drops.forEach((y, i) => {
        const char = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(char, i * 16, y * 16);
        if (y * 16 > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      });
    };

    setInterval(draw, 60);
  },

  /* ── tsParticles ── */
  initParticles() {
    if (typeof tsParticles === 'undefined') return;
    tsParticles.load("tsparticles", {
      fpsLimit: 60,
      particles: {
        number: { value: 60, density: { enable: true, area: 1000 } },
        color: { value: ["#00d9ff", "#8a2be2", "#00ff88", "#ff007f"] },
        shape: { type: "circle" },
        opacity: { value: 0.3, random: true,
          animation: { enable: true, speed: 0.5, minimumValue: 0.05, sync: false } },
        size: { value: 2, random: true,
          animation: { enable: true, speed: 2, minimumValue: 0.5, sync: false } },
        links: {
          enable: true,
          distance: 160,
          color: "#00d9ff",
          opacity: 0.08,
          width: 1
        },
        move: {
          enable: true,
          speed: 0.6,
          direction: "none",
          random: true,
          out_mode: "bounce"
        }
      },
      interactivity: {
        events: {
          onHover: { enable: true, mode: "repulse" },
          onClick: { enable: false }
        },
        modes: {
          repulse: { distance: 80, duration: 0.4 }
        }
      },
      detectRetina: true
    }).catch(() => {});
  },

  /* ── API Helpers ── */
  async fetchJSON(url) {
    try {
      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    } catch(e) {
      console.warn(`SPIDER fetch error [${url}]:`, e.message);
      return null;
    }
  },

  /* ── Counter Animation ── */
  animateCounter(el, target, duration = 1200) {
    if (!el) return;
    const start = parseInt(el.textContent.replace(/,/g,'')) || 0;
    const range = target - start;
    const step = range / (duration / 16);
    let current = start;
    const timer = setInterval(() => {
      current += step;
      if ((step > 0 && current >= target) || (step < 0 && current <= target)) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = Math.floor(current).toLocaleString();
    }, 16);
  },

  /* ── Status Badge ── */
  statusBadge(status) {
    if (status === 'success') return '<span class="badge-cyber badge-success"><i class="fas fa-check-circle"></i> Success</span>';
    if (status === 'failed')  return '<span class="badge-cyber badge-failed"><i class="fas fa-times-circle"></i> Failed</span>';
    return `<span class="badge-cyber badge-info">${status}</span>`;
  },

  levelBadge(level) {
    const map = {
      CRITICAL: 'badge-critical',
      WARNING:  'badge-warning',
      INFO:     'badge-info'
    };
    const icons = { CRITICAL: 'fa-skull', WARNING: 'fa-exclamation-triangle', INFO: 'fa-info-circle' };
    return `<span class="badge-cyber ${map[level] || 'badge-info'}"><i class="fas ${icons[level] || 'fa-info-circle'}"></i> ${level}</span>`;
  },

  eventBadge(type) {
    const map = {
      login_failed:   ['badge-failed',   'fa-times-circle',   'Failed Login'],
      login_success:  ['badge-success',  'fa-check-circle',   'Login Success'],
      brute_force:    ['badge-critical', 'fa-bolt',           'Brute Force'],
      root_login:     ['badge-root',     'fa-user-shield',    'Root Login'],
      invalid_user:   ['badge-warning',  'fa-user-times',     'Invalid User'],
      port_scan:      ['badge-warning',  'fa-search',         'Port Scan'],
    };
    const [cls, icon, label] = map[type] || ['badge-info', 'fa-question-circle', type];
    return `<span class="badge-cyber ${cls}"><i class="fas ${icon}"></i> ${label}</span>`;
  },

  flagEmoji(cc) {
    if (!cc || cc === 'XX' || cc === 'LO') return '🌐';
    return cc.toUpperCase().split('').map(c =>
      String.fromCodePoint(c.charCodeAt(0) + 127397)
    ).join('');
  },

  formatTime(ts) {
    if (!ts) return '—';
    return ts;
  },

  timeAgo(ts) {
    if (!ts) return '';
    const d = new Date(ts + (ts.includes('T') ? '' : ' UTC'));
    const diff = (Date.now() - d.getTime()) / 1000;
    if (diff < 60) return `${Math.floor(diff)}s ago`;
    if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
    return `${Math.floor(diff/86400)}d ago`;
  }
};

document.addEventListener('DOMContentLoaded', () => SPIDER.init());
window.SPIDER = SPIDER;
