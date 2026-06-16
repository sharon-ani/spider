import requests
import time
from datetime import datetime
from modules.database import db, GeoRecord

GEOIP_API = "http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp,as,lat,lon,countryCode"
_cache = {}


def lookup_ip(ip):
    """Lookup GeoIP for an IP address. Uses DB cache first."""
    if ip in ('127.0.0.1', 'localhost', '::1'):
        return _local_record()

    # Check in-memory cache
    if ip in _cache:
        if time.time() - _cache[ip]['_ts'] < 86400:
            return _cache[ip]

    # Check DB cache
    rec = GeoRecord.query.filter_by(ip=ip).first()
    if rec:
        age = (datetime.utcnow() - rec.last_updated).total_seconds()
        if age < 86400:
            d = rec.to_dict()
            _cache[ip] = {**d, '_ts': time.time()}
            return d

    # Fetch from API
    try:
        r = requests.get(GEOIP_API.format(ip=ip), timeout=3)
        data = r.json()
        if data.get('status') == 'success':
            result = {
                'ip': ip,
                'country': data.get('country', 'Unknown'),
                'country_code': data.get('countryCode', 'XX'),
                'region': data.get('regionName', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'isp': data.get('isp', 'Unknown'),
                'asn': data.get('as', 'Unknown'),
                'lat': data.get('lat'),
                'lon': data.get('lon')
            }
            # Save/update DB record
            if rec:
                for k, v in result.items():
                    setattr(rec, k, v)
                rec.last_updated = datetime.utcnow()
            else:
                rec = GeoRecord(**result)
                db.session.add(rec)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
            _cache[ip] = {**result, '_ts': time.time()}
            return result
    except Exception as e:
        print(f"[!] GeoIP lookup failed for {ip}: {e}")

    return {'ip': ip, 'country': 'Unknown', 'country_code': 'XX', 'region': 'Unknown',
            'city': 'Unknown', 'isp': 'Unknown', 'asn': 'Unknown', 'lat': None, 'lon': None}


def _local_record():
    return {'ip': '127.0.0.1', 'country': 'Local', 'country_code': 'LO',
            'region': 'Local', 'city': 'Local', 'isp': 'Local', 'asn': '', 'lat': 0, 'lon': 0}


def get_top_countries(limit=10):
    """Get top attacking countries from DB."""
    from sqlalchemy import func
    from modules.database import SSHAttempt
    results = db.session.query(
        SSHAttempt.country,
        SSHAttempt.country_code,
        func.count(SSHAttempt.id).label('count')
    ).filter(SSHAttempt.country.isnot(None)).group_by(
        SSHAttempt.country, SSHAttempt.country_code
    ).order_by(func.count(SSHAttempt.id).desc()).limit(limit).all()
    return [{'country': r.country, 'country_code': r.country_code, 'count': r.count} for r in results]


def get_attack_map_data():
    """Get lat/lon data for attack map."""
    from sqlalchemy import func
    from modules.database import SSHAttempt
    results = db.session.query(
        SSHAttempt.ip, SSHAttempt.country, SSHAttempt.lat, SSHAttempt.lon,
        func.count(SSHAttempt.id).label('count')
    ).filter(
        SSHAttempt.lat.isnot(None), SSHAttempt.lon.isnot(None)
    ).group_by(SSHAttempt.ip).order_by(func.count(SSHAttempt.id).desc()).limit(100).all()
    return [{'ip': r.ip, 'country': r.country, 'lat': r.lat, 'lon': r.lon, 'count': r.count} for r in results]
