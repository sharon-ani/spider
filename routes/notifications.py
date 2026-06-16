from flask import Blueprint, render_template
notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/')
def index():
    return render_template('notifications.html', page='notifications', title='Notifications')
