import re
import os
import threading
import time
import random
from datetime import datetime, timedelta
from modules.database import db, SSHAttempt, Incident


# Regex patterns for auth.log
FAILED_RE = re.compile(
    r'(\w+\s+\d+\s+[\d:]+).*Failed password for (?:invalid user )?(\w+) from ([\d.]+) port (\d+)'
)
SUCCESS_RE = re.compile(
    r'(\w+\s+\d+\s+[\d:]+).*Accepted (?:password|publickey) for (\w+) from ([\d.]+) port (\d+)'
)
INVALID_RE = re.compile(
    r'(\w+\s+\d+\s+[\d:]+).*Invalid user (\w+) from ([\d.]+)'
)


def parse_log_line(line):
    """Parse a single auth.log line and return SSHAttempt data or None."""
    m = FAILED_RE.search(line)
    if m:
        return {
            'timestamp': datetime.utcnow(),
            'username': m.group(2),
            'ip': m.group(3),
            'port': int(m.group(4)),
            'status': 'failed',
            'event_type': 'login_failed',
            'is_root': m.group(2) == 'root',
            'raw_log': line.strip()
        }
    m = SUCCESS_RE.search(line)
    if m:
        return {
            'timestamp': datetime.utcnow(),
            'username': m.group(2),
            'ip': m.group(3),
            'port': int(m.group(4)),
            'status': 'success',
            'event_type': 'login_success',
            'is_root': m.group(2) == 'root',
            'raw_log': line.strip()
        }
    m = INVALID_RE.search(line)
    if m:
        return {
            'timestamp': datetime.utcnow(),
            'username': m.group(2),
            'ip': m.group(3),
            'port': 22,
            'status': 'failed',
            'event_type': 'invalid_user',
            'is_root': False,
            'raw_log': line.strip()
        }
    return None


def check_brute_force(ip, app, threshold=10, window=60):
    """Check if an IP has exceeded brute-force threshold."""
    with app.app_context():
        since = datetime.utcnow() - timedelta(seconds=window)
        count = SSHAttempt.query.filter(
            SSHAttempt.ip == ip,
            SSHAttempt.status == 'failed',
            SSHAttempt.timestamp >= since
        ).count()
        return count >= threshold


def tail_log_file(log_path, app, socketio=None):
    """Tail auth.log and process new lines in real-time."""
    if not os.path.exists(log_path):
        print(f"[!] SSH log not found: {log_path} — using demo mode")
        return

    with open(log_path, 'r') as f:
        f.seek(0, 2)  # Seek to end
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            data = parse_log_line(line)
            if data:
                _save_attempt(data, app, socketio)


def _save_attempt(data, app, socketio=None):
    """Save a parsed SSH attempt to the DB and emit socket event."""
    from modules.geo_intel import lookup_ip
    with app.app_context():
        # Perform GeoIP lookup for the IP address
        geo = lookup_ip(data['ip'])
        if geo:
            data['country'] = geo.get('country')
            data['country_code'] = geo.get('country_code')
            data['region'] = geo.get('region')
            data['city'] = geo.get('city')
            data['isp'] = geo.get('isp')
            data['asn'] = geo.get('asn')
            data['lat'] = geo.get('lat')
            data['lon'] = geo.get('lon')

        attempt = SSHAttempt(**data)
        db.session.add(attempt)
        db.session.commit()

        # Check brute force
        if data['status'] == 'failed':
            if check_brute_force(data['ip'], app):
                _create_incident('CRITICAL', 'brute_force',
                    f"Brute-force attack detected from {data['ip']}", data, app)

        if data.get('is_root') and data['status'] == 'success':
            _create_incident('CRITICAL', 'root_login',
                f"Root login SUCCESS from {data['ip']}", data, app)
        elif data.get('is_root'):
            _create_incident('WARNING', 'root_login',
                f"Root login attempt from {data['ip']}", data, app)

        if socketio:
            socketio.emit('new_attack', attempt.to_dict(), namespace='/')


def _create_incident(level, etype, msg, data, app):
    with app.app_context():
        inc = Incident(
            level=level,
            event_type=etype,
            message=msg,
            ip=data.get('ip'),
            username=data.get('username')
        )
        db.session.add(inc)
        db.session.commit()


# Demo mode: inject realistic fake attacks
DEMO_IPS = [
    ("185.220.101.45", "Germany", "DE"), ("103.89.92.11", "China", "CN"),
    ("91.240.118.222", "Russia", "RU"), ("45.142.212.100", "Netherlands", "NL"),
    ("194.165.16.77", "Iran", "IR"), ("161.35.210.20", "United States", "US"),
    ("200.147.35.90", "Brazil", "BR"), ("51.178.47.248", "France", "FR"),
]
DEMO_USERS = ["root", "admin", "test", "ubuntu", "pi", "guest", "deploy", "oracle", "postgres"]


def run_demo_ssh_injector(app, socketio=None, interval=5):
    """Background thread that injects fake SSH events in demo mode."""
    def _inject():
        while True:
            time.sleep(interval)
            try:
                ip_data = random.choice(DEMO_IPS)
                ip, country, cc = ip_data
                username = random.choice(DEMO_USERS)
                status = random.choices(["failed", "success"], weights=[85, 15])[0]
                is_root = username == "root"
                evt = "login_success" if status == "success" else "login_failed"
                if is_root:
                    evt = "root_login"

                data = {
                    'timestamp': datetime.utcnow(),
                    'ip': ip,
                    'username': username,
                    'status': status,
                    'event_type': evt,
                    'country': country,
                    'country_code': cc,
                    'city': 'Unknown',
                    'is_root': is_root,
                    'is_brute_force': False,
                    'port': 22,
                    'raw_log': f'Jun 16 {datetime.utcnow().strftime("%H:%M:%S")} sshd[1234]: {"Accepted" if status=="success" else "Failed"} password for {username} from {ip} port 22 ssh2'
                }

                with app.app_context():
                    attempt = SSHAttempt(**data)
                    db.session.add(attempt)
                    db.session.commit()

                    if socketio:
                        socketio.emit('new_attack', attempt.to_dict())

            except Exception as e:
                print(f"[!] Demo injector error: {e}")

    t = threading.Thread(target=_inject, daemon=True)
    t.start()
    print("[*] Demo SSH injector started (new attack every 5s)")
