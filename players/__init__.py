from flask import Blueprint

# Create Blueprint for player management
players_bp = Blueprint('players', __name__, template_folder='templates')

# Import routes (this connects routes.py to the Blueprint)
from . import routes
