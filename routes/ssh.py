from flask import Blueprint, render_template
ssh_bp = Blueprint('ssh', __name__)

@ssh_bp.route('/')
def index():
    return render_template('ssh_monitor.html', page='ssh', title='SSH Monitoring')
