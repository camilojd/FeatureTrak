from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwd = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean(), nullable=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Client %r>' % self.name


class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client')
    target_date = db.Column(db.Date)
    url = db.Column(db.String(1000))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    area = db.relationship('Area')
    progress = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, title, description, target_date, url):
        self.title = title
        self.description = description
        self.target_date = target_date
        self.url = url

    def __repr__(self):
        return '<Feature %r>' % self.name

class Supporter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client = db.relationship('Client')
    feature = db.relationship('Feature')
    priority = db.Column(db.Integer, nullable=False)

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Area %r>' % self.name

def create_app():
    global app, db
    if app is None:
        app = Flask(__name__)
        # TODO load from external configuration file
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://enders:game@localhost/featuretrak'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

    return app
