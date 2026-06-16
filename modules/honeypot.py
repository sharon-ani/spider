import json
import os
from datetime import datetime
from modules.database import db, HoneypotSession


def parse_cowrie_log(log_path):
    """Parse Cowrie JSON log and import sessions."""
    if not os.path.exists(log_path):
        return 0

    sessions = {}
    with open(log_path, 'r') as f:
        for line in f:
            try:
                ev = json.loads(line.strip())
                sid = ev.get('session')
                if not sid:
                    continue
                if sid not in sessions:
                    sessions[sid] = {'session_id': sid, 'commands': [], 'ip': ev.get('src_ip', ''),
                                     'timestamp': ev.get('timestamp'), 'duration': 0,
                                     'username': '', 'password': '', 'login_success': False,
                                     'download_attempts': 0}
                etype = ev.get('eventid', '')
                if 'login' in etype:
                    sessions[sid]['username'] = ev.get('username', '')
                    sessions[sid]['password'] = ev.get('password', '')
                    sessions[sid]['login_success'] = 'success' in etype
                elif 'command' in etype:
                    sessions[sid]['commands'].append(ev.get('input', ''))
                elif 'closed' in etype:
                    sessions[sid]['duration'] = ev.get('duration', 0)
                elif 'download' in etype:
                    sessions[sid]['download_attempts'] += 1
            except Exception:
                pass

    count = 0
    for sid, data in sessions.items():
        existing = HoneypotSession.query.filter_by(session_id=sid).first()
        if not existing:
            h = HoneypotSession(
                session_id=sid,
                ip=data['ip'],
                username=data['username'],
                password=data['password'],
                commands=json.dumps(data['commands']),
                commands_count=len(data['commands']),
                duration=int(data['duration']),
                login_success=data['login_success'],
                download_attempts=data['download_attempts'],
                is_active=False
            )
            try:
                ts = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                h.timestamp = ts
            except Exception:
                pass
            db.session.add(h)
            count += 1

    db.session.commit()
    return count


def get_honeypot_stats():
    """Get summary statistics for honeypot sessions."""
    total = HoneypotSession.query.count()
    active = HoneypotSession.query.filter_by(is_active=True).count()
    successful = HoneypotSession.query.filter_by(login_success=True).count()

    from sqlalchemy import func
    top_users = db.session.query(
        HoneypotSession.username,
        func.count(HoneypotSession.id).label('count')
    ).filter(HoneypotSession.username.isnot(None)).group_by(
        HoneypotSession.username
    ).order_by(func.count(HoneypotSession.id).desc()).limit(5).all()

    top_passwords = db.session.query(
        HoneypotSession.password,
        func.count(HoneypotSession.id).label('count')
    ).filter(HoneypotSession.password.isnot(None)).group_by(
        HoneypotSession.password
    ).order_by(func.count(HoneypotSession.id).desc()).limit(5).all()

    return {
        'total_sessions': total,
        'active_sessions': active,
        'successful_logins': successful,
        'top_usernames': [{'username': r.username, 'count': r.count} for r in top_users],
        'top_passwords': [{'password': r.password, 'count': r.count} for r in top_passwords],
    }


def tail_cowrie_log(log_path, app, socketio=None):
    """Tail Cowrie JSON log and update/create sessions in real-time."""
    import time
    if not os.path.exists(log_path):
        print(f"[!] Cowrie honeypot log not found: {log_path} — using demo mode")
        return

    from modules.geo_intel import lookup_ip
    print(f"[*] Starting Cowrie honeypot log tailing on: {log_path}")
    with open(log_path, 'r') as f:
        f.seek(0, 2)  # Seek to end
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            try:
                ev = json.loads(line.strip())
                sid = ev.get('session')
                if not sid:
                    continue
                
                with app.app_context():
                    existing = HoneypotSession.query.filter_by(session_id=sid).first()
                    if not existing:
                        src_ip = ev.get('src_ip', '')
                        geo = lookup_ip(src_ip) if src_ip else {}
                        
                        existing = HoneypotSession(
                            session_id=sid,
                            ip=src_ip,
                            username=ev.get('username', ''),
                            password=ev.get('password', ''),
                            country=geo.get('country', 'Unknown'),
                            country_code=geo.get('country_code', 'XX'),
                            commands='[]',
                            commands_count=0,
                            duration=0,
                            login_success=False,
                            download_attempts=0,
                            is_active=True
                        )
                        try:
                            ts_str = ev.get('timestamp')
                            if ts_str:
                                existing.timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                        except Exception:
                            pass
                        db.session.add(existing)
                    
                    etype = ev.get('eventid', '')
                    if 'login' in etype:
                        existing.username = ev.get('username', existing.username)
                        existing.password = ev.get('password', existing.password)
                        existing.login_success = 'success' in etype
                    elif 'command' in etype:
                        cmds = json.loads(existing.commands or '[]')
                        cmds.append(ev.get('input', ''))
                        existing.commands = json.dumps(cmds)
                        existing.commands_count = len(cmds)
                    elif 'closed' in etype:
                        existing.duration = int(ev.get('duration', existing.duration))
                        existing.is_active = False
                    elif 'download' in etype:
                        existing.download_attempts += 1
                        
                    db.session.commit()
                    if socketio:
                        socketio.emit('new_honeypot_event', existing.to_dict())
            except Exception as e:
                print(f"[!] Error processing Cowrie log line: {e}")
