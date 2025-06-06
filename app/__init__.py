from flask import Flask
from flask_cors import CORS
from .route import register_blueprints


def create_app():
  app = Flask(__name__)
  CORS(app)
  register_blueprints(app)

  return app
