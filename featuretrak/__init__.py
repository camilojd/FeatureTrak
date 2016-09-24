from flask import Flask, abort
from models import db, User

import flask_assets
import flask_login
import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('featuretrak.default_settings')

if os.environ.has_key('FEATURETRAK_CONFIG'):
    app.config.from_envvar('FEATURETRAK_CONFIG')

db.init_app(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

assets = flask_assets.Environment()
assets.init_app(app)

@login_manager.user_loader
def user_loader(user_id):
    user = User.query.get(int(user_id))
    return user

@login_manager.unauthorized_handler
def unauthorized():
    return abort(403)

import featuretrak.views
