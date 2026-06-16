#!/usr/bin/env python3
"""
SPIDER - SSH Intelligence Dashboard
Development runner
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('DEMO_MODE', 'true')

from app import create_app, socketio

app = create_app('development')

if __name__ == '__main__':
    print("=" * 60)
    print("  SPIDER - SSH Intelligence Dashboard")
    print("  Developed by Sharon | v1.0.0")
    print("  Demo Mode: ACTIVE")
    print("=" * 60)
    print("[*] Starting SPIDER on http://0.0.0.0:5000")
    print("[*] Open your browser at: http://localhost:5000")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
