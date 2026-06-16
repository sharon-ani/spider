# 🕷️ SPIDER — SSH Intelligence Dashboard & Honeypot Monitoring

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

> **SPIDER** is a real-time cybersecurity dashboard that monitors SSH brute-force attacks, integrates with Cowrie honeypots, maps attacker locations, and sends instant alerts via WhatsApp, Telegram, and Email.

---

## ✨ Features

- 🔴 **Live Attack Feed** — Real-time SSH attack stream via Server-Sent Events
- 🌍 **Geo Intelligence** — Interactive world map showing attacker locations
- 🍯 **Honeypot Monitor** — Cowrie honeypot session tracking & credential logging
- 📊 **Analytics** — Hourly/daily/weekly attack charts and heatmaps
- 🔔 **Alerts** — WhatsApp (CallMeBot), Telegram, and Email notifications
- 📋 **Reports** — Export attack data as CSV or JSON
- 🐳 **Docker Ready** — One-command deployment with PostgreSQL & Nginx
- 🔐 **Production Secure** — Rate limiting, security headers, HTTPS/SSL support

---

## 📸 Screenshots

| Dashboard | Geo Intelligence |
|-----------|-----------------|
| ![Dashboard](https://via.placeholder.com/400x250/0d1117/00ffff?text=Dashboard) | ![Geo](https://via.placeholder.com/400x250/0d1117/00ffff?text=Geo+Map) |

---

## 🚀 Quick Start (Docker — Recommended)

### Requirements
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- Windows, Linux, or macOS

### 1. Clone the repo
```bash
git clone https://github.com/Sharon-Anil/spider.git
cd spider
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your settings (or leave defaults for demo mode)
```

### 3. Launch
```bash
docker-compose up -d --build
```

### 4. Open in browser
```
http://localhost:8080
```

That's it! 🎉 The app starts with **demo data** by default so you can explore immediately.

---

## ⚙️ Configuration (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | auto-generated |
| `DEMO_MODE` | Use fake data for testing | `true` |
| `SSH_LOG_PATH` | Path to auth.log on Linux | `/var/log/auth.log` |
| `COWRIE_LOG_PATH` | Path to Cowrie JSON log | `/cowrie/logs/cowrie.json` |
| `WHATSAPP_NUMBER` | Your WhatsApp number | — |
| `WHATSAPP_API_KEY` | CallMeBot API key | — |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | — |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | — |
| `SMTP_USERNAME` | Gmail address | — |
| `SMTP_PASSWORD` | Gmail app password | — |

---

## 🔔 WhatsApp Alerts Setup

1. Save **+34 644 82 49 96** in WhatsApp as "CallMeBot"
2. Send: `I allow callmebot to send me messages`
3. You'll receive your API key
4. Add it to `.env`: `WHATSAPP_API_KEY=your_key`
5. Restart: `docker-compose up -d`

---

## 🖥️ Bare Metal (Linux Server)

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set DEMO_MODE=false in .env for real SSH log monitoring

# Run with Gunicorn
gunicorn -c gunicorn.conf.py wsgi:app

# Or use systemd service
sudo cp spider.service /etc/systemd/system/
sudo systemctl enable --now spider
```

---

## 📁 Project Structure

```
spider/
├── app.py                  # Flask factory + background threads
├── config.py               # All configuration
├── run.py                  # Development launcher
├── wsgi.py                 # Gunicorn WSGI entrypoint
├── gunicorn.conf.py        # Gunicorn production config
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Full stack orchestration
├── nginx.conf              # Nginx reverse proxy config
├── spider.service          # Systemd service unit
│
├── modules/
│   ├── database.py         # SQLAlchemy models
│   ├── demo_data.py        # Demo data generator
│   ├── ssh_monitor.py      # Auth log parser
│   ├── honeypot.py         # Cowrie log parser
│   ├── geo_intel.py        # GeoIP lookup
│   ├── notifications.py    # WhatsApp/Telegram/Email
│   ├── analytics.py        # Data aggregations
│   └── system_monitor.py   # CPU/RAM/disk monitoring
│
├── routes/                 # 11 Flask blueprints
├── templates/              # 11 Jinja2 HTML templates
└── static/                 # CSS, JS, SVG assets
```

---

## 🔗 Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | KPI overview + live metrics |
| SSH Monitoring | `/ssh` | Attack log table |
| Live Feed | `/feed` | Real-time attack stream |
| Geo Intelligence | `/geo` | World attacker map |
| System Monitor | `/system` | CPU/RAM/disk graphs |
| Honeypot | `/honeypot` | Cowrie sessions |
| Analytics | `/analytics` | Charts & heatmap |
| Reports | `/reports` | CSV/JSON export |
| Notifications | `/notifications` | Alert settings |
| Settings | `/settings` | App configuration |

---

## 🛡️ Tech Stack

- **Backend**: Python 3.11, Flask 3.0, SQLAlchemy, Gunicorn
- **Frontend**: Vanilla JS, Chart.js, Leaflet.js, CSS3 animations
- **Database**: PostgreSQL 16 (production) / SQLite (development)
- **Infrastructure**: Docker, Nginx, Certbot (Let's Encrypt)
- **Alerts**: CallMeBot (WhatsApp), Telegram Bot API, SMTP

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Developer

Built by **Sharon Anil** | v1.0.0
