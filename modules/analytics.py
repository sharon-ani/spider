from datetime import datetime, timedelta
from sqlalchemy import func
from modules.database import db, SSHAttempt


def get_hourly_stats(hours=24):
    since = datetime.utcnow() - timedelta(hours=hours)
    if db.engine.dialect.name == 'postgresql':
        hour_col = func.to_char(SSHAttempt.timestamp, 'HH24:00').label('hour')
    else:
        hour_col = func.strftime('%H:00', SSHAttempt.timestamp).label('hour')

    results = db.session.query(
        hour_col,
        func.count(SSHAttempt.id).label('total'),
        func.sum(func.cast(SSHAttempt.status == 'failed', db.Integer)).label('failed'),
        func.sum(func.cast(SSHAttempt.status == 'success', db.Integer)).label('success')
    ).filter(SSHAttempt.timestamp >= since).group_by('hour').order_by('hour').all()
    return [{'hour': r.hour, 'total': r.total, 'failed': int(r.failed or 0), 'success': int(r.success or 0)} for r in results]


def get_daily_stats(days=30):
    since = datetime.utcnow() - timedelta(days=days)
    if db.engine.dialect.name == 'postgresql':
        date_col = func.to_char(SSHAttempt.timestamp, 'YYYY-MM-DD').label('date')
    else:
        date_col = func.strftime('%Y-%m-%d', SSHAttempt.timestamp).label('date')

    results = db.session.query(
        date_col,
        func.count(SSHAttempt.id).label('total'),
        func.sum(func.cast(SSHAttempt.status == 'failed', db.Integer)).label('failed'),
        func.sum(func.cast(SSHAttempt.status == 'success', db.Integer)).label('success')
    ).filter(SSHAttempt.timestamp >= since).group_by('date').order_by('date').all()
    return [{'date': r.date, 'total': r.total, 'failed': int(r.failed or 0), 'success': int(r.success or 0)} for r in results]


def get_weekly_stats(weeks=12):
    since = datetime.utcnow() - timedelta(weeks=weeks)
    if db.engine.dialect.name == 'postgresql':
        week_col = func.to_char(SSHAttempt.timestamp, 'IYYY-"W"IW').label('week')
    else:
        week_col = func.strftime('%Y-W%W', SSHAttempt.timestamp).label('week')

    results = db.session.query(
        week_col,
        func.count(SSHAttempt.id).label('total'),
    ).filter(SSHAttempt.timestamp >= since).group_by('week').order_by('week').all()
    return [{'week': r.week, 'total': r.total} for r in results]


def get_top_usernames(limit=10):
    results = db.session.query(
        SSHAttempt.username,
        func.count(SSHAttempt.id).label('count')
    ).group_by(SSHAttempt.username).order_by(func.count(SSHAttempt.id).desc()).limit(limit).all()
    return [{'username': r.username, 'count': r.count} for r in results]


def get_top_ips(limit=10):
    results = db.session.query(
        SSHAttempt.ip,
        SSHAttempt.country,
        SSHAttempt.country_code,
        func.count(SSHAttempt.id).label('count')
    ).group_by(
        SSHAttempt.ip,
        SSHAttempt.country,
        SSHAttempt.country_code
    ).order_by(func.count(SSHAttempt.id).desc()).limit(limit).all()
    return [{'ip': r.ip, 'country': r.country or 'Unknown', 'country_code': r.country_code or 'XX', 'count': r.count} for r in results]


def get_event_type_stats():
    results = db.session.query(
        SSHAttempt.event_type,
        func.count(SSHAttempt.id).label('count')
    ).group_by(SSHAttempt.event_type).order_by(func.count(SSHAttempt.id).desc()).all()
    return [{'event_type': r.event_type, 'count': r.count} for r in results]


def get_heatmap_data():
    """Hour-of-day x day-of-week attack heatmap."""
    if db.engine.dialect.name == 'postgresql':
        hour_col = func.to_char(SSHAttempt.timestamp, 'HH24').label('hour')
        dow_col = func.cast(func.extract('dow', SSHAttempt.timestamp), db.Integer).label('dow')
    else:
        hour_col = func.strftime('%H', SSHAttempt.timestamp).label('hour')
        dow_col = func.strftime('%w', SSHAttempt.timestamp).label('dow')

    results = db.session.query(
        hour_col,
        dow_col,
        func.count(SSHAttempt.id).label('count')
    ).group_by('hour', 'dow').all()
    data = []
    for r in results:
        data.append({'hour': int(r.hour), 'day': int(r.dow), 'count': r.count})
    return data
