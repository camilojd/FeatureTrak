from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import flask_login
import random
import string

db = SQLAlchemy()

#######################################
# SQLAlchemy models
#######################################

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwd = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean(), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    client = db.relationship('Client')

    def __repr__(self):
        return '<User %r>' % self.email

    # flask-login properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Client %r>' % self.name


class Feature(db.Model):
    __tablename__ = 'features'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    client = db.relationship('Client')
    target_date = db.Column(db.Date)
    url = db.Column(db.String(1000))
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    area = db.relationship('Area')
    progress = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<Feature %r>' % self.title

class Supporter(db.Model):
    __tablename__ = 'supporters'
    id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('features.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    client = db.relationship('Client')
    feature = db.relationship('Feature')
    priority = db.Column(db.Integer, nullable=False)

class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<Area %r>' % self.name

app = Flask(__name__)
# TODO load from external configuration file
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://enders:game@localhost/featuretrak'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'gwlUJJIqOfTpxgTFl6eBAFg3ageatqYONx39SNruIXxkLuwPY56GuGgjKZx0'
#app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
db.init_app(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(user_id):
    user = User.query.get(int(user_id))
    return user

@app.context_processor
def misc_processor():
    def random_string(chars):
       return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(chars)) 
    return dict(random_string=random_string)
