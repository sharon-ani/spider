from flask import Blueprint, render_template, jsonify, request, make_response
import csv, json, io
from datetime import datetime, timedelta
from modules.database import SSHAttempt, Incident

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
def index():
    return render_template('reports.html', page='reports', title='Reports')

@reports_bp.route('/export/csv')
def export_csv():
    since_days = request.args.get('days', 7, type=int)
    since = datetime.utcnow() - timedelta(days=since_days)
    items = SSHAttempt.query.filter(SSHAttempt.timestamp >= since).order_by(SSHAttempt.timestamp.desc()).all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['Timestamp','IP','Username','Status','Event Type','Country','City','ISP','ASN'])
    for a in items:
        writer.writerow([a.timestamp, a.ip, a.username, a.status, a.event_type,
                         a.country, a.city, a.isp, a.asn])
    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = f'attachment; filename=spider_report_{datetime.now().strftime("%Y%m%d")}.csv'
    output.headers['Content-type'] = 'text/csv'
    return output

@reports_bp.route('/export/json')
def export_json():
    since_days = request.args.get('days', 7, type=int)
    since = datetime.utcnow() - timedelta(days=since_days)
    items = SSHAttempt.query.filter(SSHAttempt.timestamp >= since).order_by(SSHAttempt.timestamp.desc()).all()
    data = [a.to_dict() for a in items]
    output = make_response(json.dumps({'generated': datetime.utcnow().isoformat(), 'count': len(data), 'data': data}, indent=2))
    output.headers['Content-Disposition'] = f'attachment; filename=spider_report_{datetime.now().strftime("%Y%m%d")}.json'
    output.headers['Content-type'] = 'application/json'
    return output
