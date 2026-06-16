import requests
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_whatsapp(phone, message, api_key=""):
    """Send WhatsApp notification via CallMeBot API."""
    try:
        url = "https://api.callmebot.com/whatsapp.php"
        params = {"phone": phone, "text": message, "apikey": api_key}
        r = requests.get(url, params=params, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[!] WhatsApp notification failed: {e}")
        return False


def send_telegram(bot_token, chat_id, message):
    """Send Telegram notification."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        r = requests.post(url, data=data, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[!] Telegram notification failed: {e}")
        return False


def send_email(smtp_server, smtp_port, username, password, to_addr, subject, body):
    """Send email notification."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = username
        msg["To"] = to_addr
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, to_addr, msg.as_string())
        return True
    except Exception as e:
        print(f"[!] Email notification failed: {e}")
        return False


def format_spider_alert(alert_type, ip, country, username=None, attempts=None, extra=None):
    """Format a SPIDER alert message."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "🕷️ SPIDER ALERT",
        "",
        f"Type: {alert_type}",
        "",
        f"IP: {ip}",
        f"Country: {country}",
    ]
    if username:
        lines.append(f"Username: {username}")
    if attempts:
        lines.append(f"Attempts: {attempts}")
    if extra:
        lines.append(f"Details: {extra}")
    lines += ["", f"Timestamp: {ts}", "", "— SPIDER SSH Intelligence Dashboard"]
    return "\n".join(lines)


def notify_async(app, incident, config_list):
    """Send notifications for an incident asynchronously."""
    def _send():
        with app.app_context():
            msg = format_spider_alert(
                alert_type=incident.event_type.replace("_", " ").title(),
                ip=incident.ip or "Unknown",
                country=incident.country or "Unknown",
                username=incident.username,
            )
            for cfg in config_list:
                if not cfg.enabled:
                    continue
                try:
                    if cfg.channel == "whatsapp":
                        send_whatsapp(cfg.target, msg, cfg.api_key or "")
                    elif cfg.channel == "telegram" and cfg.target and cfg.api_key:
                        send_telegram(cfg.target, cfg.api_key, msg)
                except Exception as e:
                    print(f"[!] Notification error ({cfg.channel}): {e}")

    t = threading.Thread(target=_send, daemon=True)
    t.start()
