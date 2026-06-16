from flask import Blueprint, render_template
system_bp = Blueprint('system', __name__)

@system_bp.route('/')
def index():
    return render_template('system_monitor.html', page='system', title='System Monitoring')
