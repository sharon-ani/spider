from flask import Blueprint, render_template
geo_bp = Blueprint('geo', __name__)

@geo_bp.route('/')
def index():
    return render_template('geo_intel.html', page='geo', title='Geo Intelligence')
