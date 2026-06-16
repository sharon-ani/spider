import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-change-in-production'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    @classmethod
    def init_app(cls, app):
        pass

    # ─── Database ──────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "spider.db")}')
    # Fix for PostgreSQL URLs from some providers (postgres:// → postgresql://)
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # ─── App Info ──────────────────────────────────────────
    APP_NAME      = "SPIDER"
    APP_TAGLINE   = "SSH Intelligence Dashboard"
    DEVELOPER     = "Sharon"
    VERSION       = "1.0.0"

    # ─── SSH Monitoring ────────────────────────────────────
    SSH_LOG_PATH           = os.environ.get('SSH_LOG_PATH', '/var/log/auth.log')
    BRUTE_FORCE_THRESHOLD  = int(os.environ.get('BRUTE_FORCE_THRESHOLD', 10))
    BRUTE_FORCE_WINDOW     = int(os.environ.get('BRUTE_FORCE_WINDOW', 60))

    # ─── GeoIP ─────────────────────────────────────────────
    GEOIP_API_URL  = "http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp,as,lat,lon,countryCode"
    GEOIP_CACHE_TTL = int(os.environ.get('GEOIP_CACHE_TTL', 86400))

    # ─── WhatsApp (CallMeBot) ──────────────────────────────
    WHATSAPP_NUMBER  = os.environ.get('WHATSAPP_NUMBER', '8281762218')
    WHATSAPP_API_KEY = os.environ.get('WHATSAPP_API_KEY', '')
    CALLMEBOT_API_URL = "https://api.callmebot.com/whatsapp.php"

    # ─── Telegram ──────────────────────────────────────────
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID   = os.environ.get('TELEGRAM_CHAT_ID', '')

    # ─── Email ─────────────────────────────────────────────
    SMTP_SERVER   = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT     = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    ALERT_EMAIL   = os.environ.get('ALERT_EMAIL', '')

    # ─── System Thresholds ─────────────────────────────────
    CPU_ALERT_THRESHOLD  = int(os.environ.get('CPU_ALERT_THRESHOLD', 80))
    RAM_ALERT_THRESHOLD  = int(os.environ.get('RAM_ALERT_THRESHOLD', 85))
    DISK_ALERT_THRESHOLD = int(os.environ.get('DISK_ALERT_THRESHOLD', 90))

    # ─── Demo / Dev ────────────────────────────────────────
    DEMO_MODE       = os.environ.get('DEMO_MODE', 'true').lower() == 'true'
    DEMO_SEED_COUNT = int(os.environ.get('DEMO_SEED_COUNT', 500))

    # ─── Cowrie ────────────────────────────────────────────
    COWRIE_LOG_PATH = os.environ.get('COWRIE_LOG_PATH',
        '/home/cowrie/cowrie/var/log/cowrie/cowrie.json')

    # ─── Session ───────────────────────────────────────────
    SESSION_COOKIE_SECURE   = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # ─── SocketIO ──────────────────────────────────────────
    SOCKETIO_ASYNC_MODE = 'threading'


class DevelopmentConfig(Config):
    DEBUG     = True
    DEMO_MODE = True
    SESSION_COOKIE_SECURE = False   # HTTP in dev


class ProductionConfig(Config):
    DEBUG     = False
    DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'
    # Enforce strong secret key in production
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        key = os.environ.get('SECRET_KEY', '')
        if not key or key == 'dev-only-change-in-production' or len(key) < 32:
            raise RuntimeError(
                "CRITICAL: Set a strong SECRET_KEY env variable (min 32 chars) for production!"
            )

    # Production logging
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        "pool_pre_ping": True,
    }


class TestingConfig(Config):
    TESTING   = True
    DEMO_MODE = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig
}
