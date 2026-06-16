from flask import Blueprint, render_template
honeypot_bp = Blueprint('honeypot', __name__)

@honeypot_bp.route('/')
def index():
    return render_template('honeypot.html', page='honeypot', title='Honeypot Sessions')
