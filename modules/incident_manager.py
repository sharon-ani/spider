from modules.database import db, Incident
from datetime import datetime


def create_incident(level, event_type, message, ip=None, username=None, country=None):
    """Create a new incident record."""
    inc = Incident(
        level=level,
        event_type=event_type,
        message=message,
        ip=ip,
        username=username,
        country=country,
        resolved=False,
        notified=False
    )
    db.session.add(inc)
    db.session.commit()
    return inc


def resolve_incident(incident_id, notes=None):
    inc = Incident.query.get(incident_id)
    if inc:
        inc.resolved = True
        inc.resolved_at = datetime.utcnow()
        if notes:
            inc.notes = notes
        db.session.commit()
        return True
    return False


def get_incident_summary():
    total = Incident.query.count()
    critical = Incident.query.filter_by(level='CRITICAL', resolved=False).count()
    warning = Incident.query.filter_by(level='WARNING', resolved=False).count()
    info = Incident.query.filter_by(level='INFO', resolved=False).count()
    resolved = Incident.query.filter_by(resolved=True).count()
    return {
        'total': total,
        'critical': critical,
        'warning': warning,
        'info': info,
        'resolved': resolved,
        'unresolved': total - resolved
    }


def get_recent_incidents(limit=20):
    incs = Incident.query.order_by(Incident.timestamp.desc()).limit(limit).all()
    return [i.to_dict() for i in incs]
