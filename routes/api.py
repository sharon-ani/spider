from flask import Blueprint, jsonify, request, Response
from datetime import datetime, timedelta
from sqlalchemy import func
import json, time

from modules.database import db, SSHAttempt, ActiveSession, SystemSnapshot, Incident, HoneypotSession, NotificationConfig, AppSetting
from modules.system_monitor import get_system_stats
from modules.analytics import get_hourly_stats, get_daily_stats, get_weekly_stats, get_top_usernames, get_top_ips, get_event_type_stats, get_heatmap_data
from modules.geo_intel import get_top_countries, get_attack_map_data
from modules.honeypot import get_honeypot_stats
from modules.incident_manager import get_incident_summary, resolve_incident

api_bp = Blueprint('api', __name__)


@api_bp.route('/stats')
def stats():
    total = SSHAttempt.query.count()
    failed = SSHAttempt.query.filter_by(status='failed').count()
    success = SSHAttempt.query.filter_by(status='success').count()
    active_sess = ActiveSession.query.filter_by(is_active=True).count()
    active_threats = Incident.query.filter_by(level='CRITICAL', resolved=False).count()
    brute_force = SSHAttempt.query.filter_by(is_brute_force=True).count()
    root_attempts = SSHAttempt.query.filter_by(is_root=True).count()
    sys_stats = get_system_stats()
    inc_summary = get_incident_summary()

    # Last 24h attacks
    since_24h = datetime.utcnow() - timedelta(hours=24)
    last_24h = SSHAttempt.query.filter(SSHAttempt.timestamp >= since_24h).count()

    return jsonify({
        'total_attempts': total,
        'failed_logins': failed,
        'success_logins': success,
        'active_sessions': active_sess,
        'active_threats': active_threats,
        'brute_force_attacks': brute_force,
        'root_attempts': root_attempts,
        'last_24h': last_24h,
        'incidents': inc_summary,
        'system': sys_stats,
        'top_countries': get_top_countries(5),
        'top_ips': get_top_ips(5),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    })


@api_bp.route('/attacks')
def attacks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status = request.args.get('status')
    country = request.args.get('country')
    event_type = request.args.get('event_type')
    search = request.args.get('search', '')

    q = SSHAttempt.query
    if status:
        q = q.filter_by(status=status)
    if country:
        q = q.filter_by(country=country)
    if event_type:
        q = q.filter_by(event_type=event_type)
    if search:
        q = q.filter(
            (SSHAttempt.ip.contains(search)) |
            (SSHAttempt.username.contains(search)) |
            (SSHAttempt.country.contains(search))
        )

    total = q.count()
    items = q.order_by(SSHAttempt.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': items.pages,
        'data': [a.to_dict() for a in items.items]
    })


@api_bp.route('/attacks/latest')
def latest_attacks():
    limit = request.args.get('limit', 20, type=int)
    items = SSHAttempt.query.order_by(SSHAttempt.timestamp.desc()).limit(limit).all()
    return jsonify([a.to_dict() for a in items])


@api_bp.route('/system')
def system():
    stats = get_system_stats()
    snapshots = SystemSnapshot.query.order_by(SystemSnapshot.timestamp.desc()).limit(30).all()
    snapshots.reverse()
    history = {
        'timestamps': [s.timestamp.strftime('%H:%M:%S') for s in snapshots],
        'cpu': [s.cpu_percent for s in snapshots],
        'ram': [s.ram_percent for s in snapshots],
        'net_in': [s.net_recv_mb for s in snapshots],
        'net_out': [s.net_sent_mb for s in snapshots],
    }
    return jsonify({'current': stats, 'history': history})


@api_bp.route('/geo')
def geo():
    return jsonify({
        'top_countries': get_top_countries(15),
        'attack_map': get_attack_map_data()
    })


@api_bp.route('/incidents')
def incidents():
    page = request.args.get('page', 1, type=int)
    level = request.args.get('level')
    resolved = request.args.get('resolved')
    q = Incident.query
    if level:
        q = q.filter_by(level=level)
    if resolved is not None:
        q = q.filter_by(resolved=(resolved == 'true'))
    total = q.count()
    items = q.order_by(Incident.timestamp.desc()).paginate(page=page, per_page=50, error_out=False)
    return jsonify({
        'total': total,
        'summary': get_incident_summary(),
        'data': [i.to_dict() for i in items.items]
    })


@api_bp.route('/incidents/<int:inc_id>/resolve', methods=['POST'])
def resolve_inc(inc_id):
    notes = request.json.get('notes', '') if request.json else ''
    ok = resolve_incident(inc_id, notes)
    return jsonify({'success': ok})


@api_bp.route('/analytics')
def analytics():
    return jsonify({
        'hourly': get_hourly_stats(24),
        'daily': get_daily_stats(30),
        'weekly': get_weekly_stats(12),
        'top_usernames': get_top_usernames(10),
        'top_ips': get_top_ips(10),
        'event_types': get_event_type_stats(),
        'heatmap': get_heatmap_data(),
        'top_countries': get_top_countries(10),
    })


@api_bp.route('/honeypot')
def honeypot():
    page = request.args.get('page', 1, type=int)
    q = HoneypotSession.query.order_by(HoneypotSession.timestamp.desc())
    total = q.count()
    items = q.paginate(page=page, per_page=50, error_out=False)
    return jsonify({
        'total': total,
        'stats': get_honeypot_stats(),
        'data': [s.to_dict() for s in items.items]
    })


@api_bp.route('/sessions')
def sessions():
    active = ActiveSession.query.filter_by(is_active=True).all()
    recent = ActiveSession.query.order_by(ActiveSession.start_time.desc()).limit(20).all()
    return jsonify({
        'active': [s.to_dict() for s in active],
        'recent': [s.to_dict() for s in recent]
    })


@api_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        all_s = AppSetting.query.all()
        return jsonify({s.key: s.value for s in all_s})
    data = request.json or {}
    for key, value in data.items():
        s = AppSetting.query.filter_by(key=key).first()
        if s:
            s.value = str(value)
            s.updated_at = datetime.utcnow()
        else:
            db.session.add(AppSetting(key=key, value=str(value)))
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/notifications/config', methods=['GET', 'POST'])
def notif_config():
    if request.method == 'GET':
        cfgs = NotificationConfig.query.all()
        return jsonify([c.to_dict() for c in cfgs])
    data = request.json or {}
    channel = data.get('channel')
    cfg = NotificationConfig.query.filter_by(channel=channel).first()
    if not cfg:
        cfg = NotificationConfig(channel=channel)
        db.session.add(cfg)
    for k, v in data.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    cfg.last_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/notifications/test', methods=['POST'])
def test_notifications():
    from modules.notifications import send_whatsapp, send_telegram, format_spider_alert
    
    cfgs = NotificationConfig.query.filter_by(enabled=True).all()
    if not cfgs:
        return jsonify({'success': False, 'message': 'No notification channels are currently enabled!'}), 400
        
    msg = format_spider_alert(
        alert_type="Test Alert",
        ip="203.0.113.10",
        country="Germany",
        username="root",
        extra="This is a manual test alert triggered from the SPIDER notifications panel."
    )
    
    sent = []
    errors = []
    for cfg in cfgs:
        try:
            if cfg.channel == "whatsapp":
                ok = send_whatsapp(cfg.target, msg, cfg.api_key or "")
                if ok:
                    sent.append("WhatsApp")
                else:
                    errors.append("WhatsApp (invalid number or API key)")
            elif cfg.channel == "telegram" and cfg.target and cfg.api_key:
                ok = send_telegram(cfg.target, cfg.api_key, msg)
                if ok:
                    sent.append("Telegram")
                else:
                    errors.append("Telegram (invalid token or chat ID)")
        except Exception as e:
            errors.append(f"{cfg.channel}: {str(e)}")
            
    if errors and not sent:
        return jsonify({'success': False, 'message': f"Failed to send alerts: {', '.join(errors)}"}), 200
        
    return jsonify({
        'success': True,
        'message': f"Test alert sent via {', '.join(sent)}." + (f" Errors: {', '.join(errors)}" if errors else "")
    })


@api_bp.route('/stream')
def stream():
    """SSE stream for real-time attack events."""
    def event_stream():
        last_id = SSHAttempt.query.count()
        while True:
            time.sleep(4)
            new_items = SSHAttempt.query.filter(SSHAttempt.id > last_id).order_by(SSHAttempt.timestamp.asc()).limit(5).all()
            for item in new_items:
                last_id = item.id
                yield f"data: {json.dumps(item.to_dict())}\n\n"
    return Response(event_stream(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})
