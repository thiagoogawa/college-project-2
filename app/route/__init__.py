from flask import Blueprint
from .user import user_routes
from .main import main_route

def register_blueprints(app):
    app.register_blueprint(user_routes, url_prefix = '/users')
    app.register_blueprint(main_route)
