import psutil
import platform
import os
import time
from datetime import datetime
from modules.database import db, SystemSnapshot


def get_system_stats():
    """Collect real-time system stats using psutil."""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()

    # Load averages (Linux only)
    load_avg = [0, 0, 0]
    try:
        load_avg = list(os.getloadavg())
    except (AttributeError, OSError):
        load_avg = [cpu/100, cpu/100, cpu/100]

    # Uptime
    boot_ts = psutil.boot_time()
    uptime_s = int(time.time() - boot_ts)

    # Net speeds (since last snapshot) - simplified
    net_in_mb = round(net.bytes_recv / 1024 / 1024, 2)
    net_out_mb = round(net.bytes_sent / 1024 / 1024, 2)

    return {
        'cpu_percent': round(cpu, 1),
        'ram_percent': round(mem.percent, 1),
        'ram_used_gb': round(mem.used / 1e9, 2),
        'ram_total_gb': round(mem.total / 1e9, 2),
        'disk_percent': round(disk.percent, 1),
        'disk_used_gb': round(disk.used / 1e9, 2),
        'disk_total_gb': round(disk.total / 1e9, 2),
        'net_sent_mb': net_out_mb,
        'net_recv_mb': net_in_mb,
        'net_bytes_sent': net.bytes_sent,
        'net_bytes_recv': net.bytes_recv,
        'load_avg_1': round(load_avg[0], 2),
        'load_avg_5': round(load_avg[1], 2),
        'load_avg_15': round(load_avg[2], 2),
        'uptime_seconds': uptime_s,
        'uptime_str': format_uptime(uptime_s),
        'platform': platform.system(),
        'hostname': platform.node(),
        'cpu_count': psutil.cpu_count(),
        'cpu_freq': _get_cpu_freq(),
        'processes': len(psutil.pids()),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }


def _get_cpu_freq():
    try:
        freq = psutil.cpu_freq()
        return round(freq.current, 0) if freq else 0
    except Exception:
        return 0


def format_uptime(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def get_running_services():
    """Get list of running processes (top 15 by CPU)."""
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            procs.append({
                'pid': p.info['pid'],
                'name': p.info['name'],
                'cpu': round(p.info['cpu_percent'] or 0, 1),
                'mem': round(p.info['memory_percent'] or 0, 1),
                'status': p.info['status']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x['cpu'], reverse=True)
    return procs[:15]


def get_cpu_history(snapshots):
    """Extract CPU history from snapshots list."""
    return [{'t': s.timestamp.strftime('%H:%M:%S'), 'v': s.cpu_percent} for s in snapshots]


def get_network_interfaces():
    """Get network interfaces info."""
    ifaces = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for iface, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == 2:  # AF_INET (IPv4)
                s = stats.get(iface)
                ifaces.append({
                    'interface': iface,
                    'ip': addr.address,
                    'netmask': addr.netmask,
                    'speed': s.speed if s else 0,
                    'is_up': s.isup if s else False
                })
    return ifaces


def save_snapshot(app):
    """Save a system snapshot to DB (called by background thread)."""
    with app.app_context():
        stats = get_system_stats()
        snap = SystemSnapshot(
            cpu_percent=stats['cpu_percent'],
            ram_percent=stats['ram_percent'],
            ram_used_gb=stats['ram_used_gb'],
            ram_total_gb=stats['ram_total_gb'],
            disk_percent=stats['disk_percent'],
            disk_used_gb=stats['disk_used_gb'],
            disk_total_gb=stats['disk_total_gb'],
            net_bytes_sent=stats['net_bytes_sent'],
            net_bytes_recv=stats['net_bytes_recv'],
            net_sent_mb=stats['net_sent_mb'],
            net_recv_mb=stats['net_recv_mb'],
            load_avg_1=stats['load_avg_1'],
            load_avg_5=stats['load_avg_5'],
            load_avg_15=stats['load_avg_15'],
        )
        db.session.add(snap)
        db.session.commit()
        # Keep only last 200 snapshots
        count = SystemSnapshot.query.count()
        if count > 200:
            oldest = SystemSnapshot.query.order_by(SystemSnapshot.timestamp.asc()).limit(count - 200).all()
            for o in oldest:
                db.session.delete(o)
            db.session.commit()
