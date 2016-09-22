from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy

import config
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

    def is_valid(self, request):
        ret = []
        # toy validation
        # First check key, then check key value
        if 'username' in request:
            if '@' in request['username']:
                ret.append('The username cannot contain an "at" sign (@)')
        if 'email' in request:
            if not '@' in request['email']:
                ret.append('The email address is invalid')
        if 'is_admin' in request:
            # admins don't belong to a client, non admins should always belong to one
            if request['is_admin'] is True:
                if self.client_id is not None:
                    ret.append("There shouldn't be a client assigned to an Administrator")
            else:
                if not request.has_key('client_id'):
                    ret.append('User should be assigned to a client')

        return ret

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
    weight = db.Column(db.Numeric(precision=5, scale=2), nullable=False, default=1)

    def is_valid(self, request):
        ret = []
        if 'weight' in request:
            try:
                float(request['weight'])
            except ValueError as e:
                ret.append('Client should have a valid numeric weight')

        return ret

    def to_dict(self):
        row = {}
        row['id'] = self.id
        row['name'] = self.name
        row['weight'] = str(self.weight)
        return row

    def __repr__(self):
        return '<Client %r>' % self.name


class Feature(db.Model):
    __tablename__ = 'features'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    # feature owner
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    client = db.relationship('Client')
    target_date = db.Column(db.Date)
    url = db.Column(db.String(1000))
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    area = db.relationship('Area')
    is_public = db.Column(db.Boolean(), nullable=False, default=False)

    def to_dict(self, include_supporters=False):
        row = {}
        row['id'] = self.id
        row['description'] = self.description
        row['is_public'] = self.is_public
        row['target_date'] = '' if self.target_date is None else self.target_date.strftime('%Y-%m-%d')
        row['title'] = self.title
        row['url'] = self.url
        row['area'] = self.area.name
        row['area_id'] = self.area.id
        row['client_name'] = self.client.name
        row['client_id'] = self.client.id
        if include_supporters:
            # may be possible to configure SA to lazily load this...
            row['supporters_cnt'] = len(self.supporters)
            row['supporters_names'] = ', '.join([k.client.name for k in self.supporters])
        return row

    def __repr__(self):
        return '<Feature %r>' % self.title

class Supporter(db.Model):
    __tablename__ = 'supporters'
    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('features.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    client = db.relationship('Client')
    feature = db.relationship('Feature', backref='supporters')
    priority = db.Column(db.Integer, nullable=False)

class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<Area %r>' % self.name

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = config.FLASK_SECRET_KEY
db.init_app(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(user_id):
    user = User.query.get(int(user_id))
    return user

@login_manager.unauthorized_handler
def unauthorized():
    return abort(403)

@app.context_processor
def misc_processor():
    def random_string(chars):
       return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(chars)) 
    return dict(random_string=random_string)
