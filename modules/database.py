from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SSHAttempt(db.Model):
    __tablename__ = 'ssh_attempts'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip = db.Column(db.String(45), nullable=False, index=True)
    username = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success / failed
    event_type = db.Column(db.String(50), default='login_attempt')
    country = db.Column(db.String(100))
    country_code = db.Column(db.String(5))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    isp = db.Column(db.String(200))
    asn = db.Column(db.String(100))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    is_root = db.Column(db.Boolean, default=False)
    is_brute_force = db.Column(db.Boolean, default=False)
    port = db.Column(db.Integer, default=22)
    raw_log = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'ip': self.ip,
            'username': self.username,
            'status': self.status,
            'event_type': self.event_type,
            'country': self.country or 'Unknown',
            'country_code': self.country_code or 'XX',
            'region': self.region or 'Unknown',
            'city': self.city or 'Unknown',
            'isp': self.isp or 'Unknown',
            'asn': self.asn or 'Unknown',
            'lat': self.lat,
            'lon': self.lon,
            'is_root': self.is_root,
            'is_brute_force': self.is_brute_force,
            'port': self.port
        }


class ActiveSession(db.Model):
    __tablename__ = 'active_sessions'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer, default=0)  # seconds
    country = db.Column(db.String(100))
    country_code = db.Column(db.String(5))
    is_active = db.Column(db.Boolean, default=True)
    pid = db.Column(db.Integer)

    def to_dict(self):
        dur = self.duration or 0
        if self.is_active and self.start_time:
            dur = int((datetime.utcnow() - self.start_time).total_seconds())
        return {
            'id': self.id,
            'ip': self.ip,
            'username': self.username,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'duration': dur,
            'duration_str': f"{dur//3600}h {(dur%3600)//60}m {dur%60}s",
            'country': self.country or 'Unknown',
            'country_code': self.country_code or 'XX',
            'is_active': self.is_active
        }


class SystemSnapshot(db.Model):
    __tablename__ = 'system_snapshots'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    cpu_percent = db.Column(db.Float, default=0)
    ram_percent = db.Column(db.Float, default=0)
    ram_used_gb = db.Column(db.Float, default=0)
    ram_total_gb = db.Column(db.Float, default=0)
    disk_percent = db.Column(db.Float, default=0)
    disk_used_gb = db.Column(db.Float, default=0)
    disk_total_gb = db.Column(db.Float, default=0)
    net_bytes_sent = db.Column(db.BigInteger, default=0)
    net_bytes_recv = db.Column(db.BigInteger, default=0)
    net_sent_mb = db.Column(db.Float, default=0)
    net_recv_mb = db.Column(db.Float, default=0)
    load_avg_1 = db.Column(db.Float, default=0)
    load_avg_5 = db.Column(db.Float, default=0)
    load_avg_15 = db.Column(db.Float, default=0)

    def to_dict(self):
        return {
            'timestamp': self.timestamp.strftime('%H:%M:%S') if self.timestamp else None,
            'cpu_percent': round(self.cpu_percent, 1),
            'ram_percent': round(self.ram_percent, 1),
            'ram_used_gb': round(self.ram_used_gb, 2),
            'ram_total_gb': round(self.ram_total_gb, 2),
            'disk_percent': round(self.disk_percent, 1),
            'disk_used_gb': round(self.disk_used_gb, 2),
            'disk_total_gb': round(self.disk_total_gb, 2),
            'net_sent_mb': round(self.net_sent_mb, 2),
            'net_recv_mb': round(self.net_recv_mb, 2),
            'load_avg_1': round(self.load_avg_1, 2),
            'load_avg_5': round(self.load_avg_5, 2),
            'load_avg_15': round(self.load_avg_15, 2),
        }


class GeoRecord(db.Model):
    __tablename__ = 'geo_records'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), unique=True, nullable=False, index=True)
    country = db.Column(db.String(100))
    country_code = db.Column(db.String(5))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    isp = db.Column(db.String(200))
    asn = db.Column(db.String(100))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'ip': self.ip,
            'country': self.country,
            'country_code': self.country_code,
            'region': self.region,
            'city': self.city,
            'isp': self.isp,
            'asn': self.asn,
            'lat': self.lat,
            'lon': self.lon
        }


class HoneypotSession(db.Model):
    __tablename__ = 'honeypot_sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))
    country = db.Column(db.String(100))
    country_code = db.Column(db.String(5))
    duration = db.Column(db.Integer, default=0)
    commands = db.Column(db.Text)  # JSON list
    is_active = db.Column(db.Boolean, default=False)
    commands_count = db.Column(db.Integer, default=0)
    download_attempts = db.Column(db.Integer, default=0)
    login_success = db.Column(db.Boolean, default=False)

    def to_dict(self):
        import json
        cmds = []
        try:
            cmds = json.loads(self.commands) if self.commands else []
        except Exception:
            pass
        return {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'ip': self.ip,
            'username': self.username or 'N/A',
            'password': self.password or 'N/A',
            'country': self.country or 'Unknown',
            'country_code': self.country_code or 'XX',
            'duration': self.duration or 0,
            'commands': cmds,
            'commands_count': self.commands_count or 0,
            'download_attempts': self.download_attempts or 0,
            'login_success': self.login_success,
            'is_active': self.is_active
        }


class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    level = db.Column(db.String(20), nullable=False)  # INFO / WARNING / CRITICAL
    event_type = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    ip = db.Column(db.String(45))
    username = db.Column(db.String(100))
    country = db.Column(db.String(100))
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    notified = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'level': self.level,
            'event_type': self.event_type,
            'message': self.message,
            'ip': self.ip or 'N/A',
            'username': self.username or 'N/A',
            'country': self.country or 'Unknown',
            'resolved': self.resolved,
            'notes': self.notes or ''
        }


class NotificationConfig(db.Model):
    __tablename__ = 'notification_configs'
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(50), nullable=False)  # whatsapp/telegram/email
    target = db.Column(db.String(500))
    api_key = db.Column(db.String(500))
    enabled = db.Column(db.Boolean, default=False)
    on_failed_login = db.Column(db.Boolean, default=True)
    on_success_login = db.Column(db.Boolean, default=True)
    on_root_login = db.Column(db.Boolean, default=True)
    on_brute_force = db.Column(db.Boolean, default=True)
    on_new_country = db.Column(db.Boolean, default=True)
    on_critical = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'channel': self.channel,
            'target': self.target,
            'enabled': self.enabled,
            'on_failed_login': self.on_failed_login,
            'on_success_login': self.on_success_login,
            'on_root_login': self.on_root_login,
            'on_brute_force': self.on_brute_force,
            'on_new_country': self.on_new_country,
            'on_critical': self.on_critical
        }


class AppSetting(db.Model):
    __tablename__ = 'app_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
