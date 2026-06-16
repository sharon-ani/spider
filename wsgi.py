#!/usr/bin/env python3
"""
SPIDER — WSGI entry point for Gunicorn / uWSGI
Usage: gunicorn -c gunicorn.conf.py wsgi:app
"""
from app import create_app

app = create_app('production')

if __name__ == '__main__':
    app.run()
