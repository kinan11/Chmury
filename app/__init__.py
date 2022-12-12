
from flask import Flask, current_app

import os

app = Flask(__name__)
from app import routes

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY