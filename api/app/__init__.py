import sys
import os
from flask import Flask
from .routes import bp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from shared.config.config import flask_config

app = Flask(__name__)
app.config.from_object(flask_config)

app.register_blueprint(bp)