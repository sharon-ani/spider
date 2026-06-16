from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import threading
import time
import os

from config import config
from modules.database import db
from modules.demo_data import seed_database
from modules.system_monitor import save_snapshot
from modules.ssh_monitor import run_demo_ssh_injector

socketio = SocketIO()


def create_app(config_name='default'):
    app = Flask(__name__)
    cfg = config[config_name]
    app.config.from_object(cfg)
    cfg.init_app(app)

    # Init extensions
    db.init_app(app)
    CORS(app)
    socketio.init_app(app, async_mode='threading', cors_allowed_origins='*')

    with app.app_context():
        db.create_all()
        if app.config.get('DEMO_MODE', True):
            seed_database(app, app.config.get('DEMO_SEED_COUNT', 500))

    # Register blueprints
    from routes.dashboard import dashboard_bp
    from routes.api import api_bp
    from routes.ssh import ssh_bp
    from routes.attack_feed import feed_bp
    from routes.geo import geo_bp
    from routes.system import system_bp
    from routes.honeypot import honeypot_bp
    from routes.analytics import analytics_bp
    from routes.reports import reports_bp
    from routes.notifications import notifications_bp
    from routes.settings import settings_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ssh_bp, url_prefix='/ssh')
    app.register_blueprint(feed_bp, url_prefix='/feed')
    app.register_blueprint(geo_bp, url_prefix='/geo')
    app.register_blueprint(system_bp, url_prefix='/system')
    app.register_blueprint(honeypot_bp, url_prefix='/honeypot')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    # Background threads
    _start_background_threads(app)

    return app


def _start_background_threads(app):
    """Start system snapshot collector and demo SSH injector."""
    demo_mode = app.config.get('DEMO_MODE', True)

    def snapshot_worker():
        while True:
            try:
                save_snapshot(app)
            except Exception as e:
                print(f"[!] Snapshot error: {e}")
            time.sleep(5)

    t = threading.Thread(target=snapshot_worker, daemon=True)
    t.start()

    if demo_mode:
        run_demo_ssh_injector(app, socketio, interval=6)
    else:
        # Launch real SSH log tailing
        from modules.ssh_monitor import tail_log_file
        ssh_log = app.config.get('SSH_LOG_PATH', '/var/log/auth.log')
        t_ssh = threading.Thread(target=tail_log_file, args=(ssh_log, app, socketio), daemon=True)
        t_ssh.start()

        # Launch real Cowrie honeypot log tailing
        from modules.honeypot import tail_cowrie_log
        cowrie_log = app.config.get('COWRIE_LOG_PATH')
        if cowrie_log:
            t_cowrie = threading.Thread(target=tail_cowrie_log, args=(cowrie_log, app, socketio), daemon=True)
            t_cowrie.start()
