# 🕷️ SPIDER — SSH Intelligence Dashboard & Honeypot Monitoring

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

> **SPIDER** is a real-time cybersecurity dashboard that monitors SSH brute-force attacks, integrates with Cowrie honeypots, maps attacker locations worldwide, and sends instant alerts via WhatsApp, Telegram, and Email.

---

## ✨ Features

- 🔴 **Live Attack Feed** — Real-time SSH attack stream via Server-Sent Events
- 🌍 **Geo Intelligence** — Interactive world map showing attacker locations
- 🍯 **Honeypot Monitor** — Cowrie honeypot session tracking & credential logging
- 📊 **Analytics** — Hourly/daily/weekly attack charts and heatmaps
- 🔔 **Smart Alerts** — WhatsApp (CallMeBot), Telegram, and Email notifications
- 📋 **Reports** — Export attack data as CSV or JSON
- 🐳 **Docker Ready** — One-command deployment with PostgreSQL & Nginx
- 🔐 **Production Secure** — Rate limiting, security headers, HTTPS/SSL support

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
│   ├── database.py         # SQLAlchemy models (7 tables)
│   ├── demo_data.py        # Demo data generator
│   ├── ssh_monitor.py      # Auth log real-time parser
│   ├── honeypot.py         # Cowrie JSON log parser
│   ├── geo_intel.py        # GeoIP lookup via ip-api.com
│   ├── notifications.py    # WhatsApp / Telegram / Email
│   ├── analytics.py        # Data aggregations & charts
│   └── system_monitor.py   # CPU / RAM / disk monitoring
│
├── routes/                 # 11 Flask blueprints
├── templates/              # 11 Jinja2 HTML templates
└── static/                 # CSS, JS, SVG assets
```

---

## 🔗 Dashboard Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | KPI overview + live metrics |
| SSH Monitoring | `/ssh` | Full attack log table |
| Live Feed | `/feed` | Real-time attack stream |
| Geo Intelligence | `/geo` | World attacker map |
| System Monitor | `/system` | CPU / RAM / disk graphs |
| Honeypot | `/honeypot` | Cowrie sessions & credentials |
| Analytics | `/analytics` | Charts & attack heatmap |
| Reports | `/reports` | CSV / JSON export |
| Notifications | `/notifications` | Alert channel settings |
| Settings | `/settings` | App configuration |

---

## 🛡️ Tech Stack

- **Backend**: Python 3.11, Flask 3.0, SQLAlchemy, Gunicorn
- **Frontend**: Vanilla JS, Chart.js, Leaflet.js, CSS3 animations
- **Database**: PostgreSQL 16 (production) / SQLite (development)
- **Infrastructure**: Docker, Nginx, Certbot (Let's Encrypt)
- **Alerts**: CallMeBot (WhatsApp), Telegram Bot API, SMTP

---

---

# 🚀 INSTALLATION GUIDE

---

## ⚡ Option 1 — Quick Start (Windows / Mac / Linux with Docker)

### Requirements
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/sharon-ani/dearcomrade.git
cd dearcomrade

# 2. Copy and configure environment file
cp .env.example .env
# Edit .env if needed (defaults work for demo mode)

# 3. Launch all services
docker-compose up -d --build

# 4. Open in browser
# http://localhost:8080
```

> ✅ App starts with **demo data** by default — explore everything immediately!

---

## 🔬 Option 2 — Full Cybersecurity Lab (Ubuntu + Kali Linux in VirtualBox)

This setup lets you run **real SSH attacks from Kali** and watch SPIDER capture them live on Ubuntu.

```
Windows (Host)
├── Ubuntu VM  ← Target server — runs SPIDER
└── Kali VM    ← Attacker machine — runs hydra / nmap
```

---

### 🔧 Part A — VirtualBox Network Setup

> ⚠️ **Critical step** — both VMs must be on the same network to communicate.

**For BOTH VMs (Ubuntu and Kali):**

1. Open **VirtualBox** on Windows
2. Right-click the VM → **Settings** → **Network**
3. Adapter 1 → Attached to: **Host-Only Adapter**
4. Name: `VirtualBox Host-Only Ethernet Adapter`
5. Click **OK**
6. Repeat for the other VM

---

### 🖥️ Part B — Setup Ubuntu VM (Target)

Boot your Ubuntu VM and open a terminal:

#### 1. Find Ubuntu's IP address
```bash
ip a
# Look for an IP like: 192.168.56.101
# Write this down — you'll need it for Kali attacks!
```

#### 2. Install and enable SSH
```bash
sudo apt update
sudo apt install openssh-server git -y
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
# Should show: Active (running) ✅
```

#### 3. Install Docker
```bash
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

#### 4. Clone and configure SPIDER
```bash
git clone https://github.com/sharon-ani/dearcomrade.git
cd dearcomrade
cp .env.example .env
nano .env
```

**Change these lines in the editor:**
```env
DEMO_MODE=false              # ← Real data mode
SSH_LOG_PATH=/var/log/auth.log
FLASK_ENV=production
```
> Press `Ctrl+X` → `Y` → `Enter` to save

#### 5. Allow SPIDER to read SSH logs
```bash
sudo chmod o+r /var/log/auth.log
```

#### 6. Launch SPIDER
```bash
docker-compose up -d --build
# First launch takes ~3 minutes (downloads Docker images)
```

#### 7. Verify it's running
```bash
docker ps
# Should show 4 containers: spider_app, spider_nginx, spider_db, spider_certbot
```

#### 8. Open the dashboard

- From Ubuntu browser: `http://localhost:8080`
- From Windows browser: `http://192.168.56.101:8080`

---

### ⚔️ Part C — Attack from Kali Linux

Boot your Kali VM and open a terminal:

#### 1. Verify you can reach Ubuntu
```bash
ping 192.168.56.101
# Replace with your actual Ubuntu IP
# Should get replies ✅
```

#### 2. Scan open ports on Ubuntu
```bash
nmap -sV -p 22 192.168.56.101
# Should show: 22/tcp open  ssh ✅
```

#### 3. Prepare the password wordlist
```bash
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
# (Only needed if not already unzipped)
```

#### 4. Attack — Hydra SSH brute force
```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt \
      192.168.56.101 ssh -t 4 -V
```
> `-l root` = target username  
> `-P rockyou.txt` = famous password list (14 million passwords)  
> `-t 4` = 4 parallel threads  
> `-V` = show every attempt

#### 5. Attack — Multiple usernames and passwords
```bash
hydra -L /usr/share/wordlists/metasploit/unix_users.txt \
      -P /usr/share/wordlists/metasploit/unix_passwords.txt \
      192.168.56.101 ssh -t 4
```

#### 6. Attack — Nmap SSH brute script
```bash
nmap -sV --script ssh-brute 192.168.56.101 -p 22
```

#### 7. Attack — Medusa (fast brute force)
```bash
medusa -h 192.168.56.101 -u admin \
       -P /usr/share/wordlists/rockyou.txt -M ssh
```

---

### 📊 Part D — Watch Attacks in SPIDER Dashboard

Go to `http://localhost:8080` on Ubuntu (or `http://192.168.56.101:8080` from Windows):

| Page | What You'll See During Attack |
|------|-------------------------------|
| 🏠 **Dashboard** | Failed logins counter climbing in real time |
| ⚡ **Live Feed** | Each Kali attempt appears within seconds |
| 🔍 **SSH Monitor** | Kali's IP listed with every username tried |
| 🌍 **Geo Intel** | Attack source plotted on world map |
| 📊 **Analytics** | Spike in hourly attack chart |
| 🔔 **Notifications** | WhatsApp / Telegram alert fired if configured |

---

### ✅ Troubleshooting

| Problem | Solution |
|---------|----------|
| VMs can't ping each other | Ensure both VMs use **Host-Only Adapter** in VirtualBox |
| SPIDER won't start | Run `docker-compose logs spider` to see errors |
| No attacks showing in dashboard | Confirm `DEMO_MODE=false` in `.env` |
| `auth.log` permission denied | Run `sudo chmod o+r /var/log/auth.log` |
| `git` not found on Ubuntu | `sudo apt install git -y` |
| Port 8080 not accessible | Check `docker ps` — nginx container must be running |
| Hydra not installed on Kali | `sudo apt install hydra -y` |

---

## 🏭 Option 3 — Bare Metal Linux Server (Production)

For deploying on a real internet-facing Linux VPS:

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env   # Set DEMO_MODE=false, SSH_LOG_PATH, etc.

# Run with Gunicorn
gunicorn -c gunicorn.conf.py wsgi:app

# Or install as a systemd service (runs on boot)
sudo cp spider.service /etc/systemd/system/
sudo systemctl enable --now spider
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key (must be 32+ chars in production) | auto-generated |
| `DEMO_MODE` | `true` = fake data, `false` = real SSH logs | `true` |
| `SSH_LOG_PATH` | Path to SSH auth log on Linux | `/var/log/auth.log` |
| `COWRIE_LOG_PATH` | Path to Cowrie honeypot JSON log | `/cowrie/logs/cowrie.json` |
| `DATABASE_URL` | Database connection string | PostgreSQL (Docker) |
| `WHATSAPP_NUMBER` | Your WhatsApp number (without +) | — |
| `WHATSAPP_API_KEY` | CallMeBot API key | — |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | — |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | — |
| `SMTP_USERNAME` | Gmail address for email alerts | — |
| `SMTP_PASSWORD` | Gmail app password | — |
| `CPU_ALERT_THRESHOLD` | CPU % to trigger alert | `80` |
| `RAM_ALERT_THRESHOLD` | RAM % to trigger alert | `85` |
| `DISK_ALERT_THRESHOLD` | Disk % to trigger alert | `90` |

---

## 🔔 WhatsApp Alerts Setup

1. Save **+34 644 82 49 96** in WhatsApp contacts as `CallMeBot`
2. Send them this exact message: `I allow callmebot to send me messages`
3. They reply with your API key (e.g. `1234567`)
4. Add to `.env`:
   ```env
   WHATSAPP_NUMBER=your_number_without_plus
   WHATSAPP_API_KEY=1234567
   ```
5. Restart: `docker-compose up -d`
6. Test at: `http://localhost:8080/notifications` → click **Send Test Now**

---

## 🔒 SSL / HTTPS Setup (Production with Domain)

1. Point your domain's `A record` → your server's public IP
2. Edit `nginx.conf` — uncomment the SSL server block
3. Run Certbot:
   ```bash
   docker-compose exec certbot certbot certonly \
     --webroot --webroot-path=/var/www/certbot \
     -d yourdomain.com
   ```
4. Restart nginx: `docker-compose restart nginx`

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Developer

Built by **Sharon Anil** | v1.0.0

> ⚠️ **Legal Notice**: Only use SPIDER to monitor systems you own or have explicit permission to monitor. Only perform attack simulations on machines you own in a private lab environment.
