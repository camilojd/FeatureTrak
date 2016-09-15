from flask import render_template, jsonify, request, make_response
from database import app, db, User, Client, Area
import flask_login

# helper
def make_sa_row_dict(obj):
    d = dict(obj.__dict__)
    d.pop('_sa_instance_state', None)
    return d

# main view
@app.route('/')
def index():
    return render_template('base.html')

@app.route('/api/v1/status')
def status():
    user = flask_login.current_user
    status = {}
    if user.is_authenticated:
        status['username'] = user.username
        status['full_name'] = user.full_name

    return jsonify(status)

@app.route('/api/v1/login', methods=['POST'])
def login():
    criteria = {}
    if '@' in request.json['username']:
        criteria['email'] = request.json['username']
    else:
        criteria['username'] = request.json['username']
    user = User.query.filter_by(**criteria).first() 
    if user is None:
        return jsonify({'success': False, 'msj': 'Invalid credentials'})

    # any password is valid...
    flask_login.login_user(user)
    return jsonify({'success' : True})

@app.route('/api/v1/logout', methods=['POST'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return jsonify({'success' : True})

@app.route('/whoami')
@flask_login.login_required
def whoami():
    return flask_login.current_user.full_name

# API views
# Clients
@app.route('/api/v1/admin/clients', methods=['GET'])
@flask_login.login_required
def client_list():
    clients = [make_sa_row_dict(r) for r in Client.query.all()]

    return jsonify(clients)

@app.route('/api/v1/admin/client', methods=['POST'])
@flask_login.login_required
def client_create():
    obj = Client()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/client/<int:client_id>', methods=['GET', 'PUT', 'DELETE'])
@flask_login.login_required
def client_get_update_or_delete(client_id):
    obj = Client.query.get_or_404(client_id)
    if request.method == 'GET':
        return jsonify(make_sa_row_dict(obj))

    ret = {}
    try:
        if request.method == 'PUT':
            # could validate data here...
            for k, v in request.json.iteritems():
                setattr(obj, k, v)
        else:
            db.session.delete(obj)

        db.session.commit()
    except Exception as e:
        # may fail due to FK constraints, field validation, etc
        ret['msj'] = str(e)

        return make_response(jsonify(ret), 409)

    return jsonify(ret)

# Areas
@app.route('/api/v1/admin/areas', methods=['GET'])
@flask_login.login_required
def area_list():
    areas = [make_sa_row_dict(r) for r in Area.query.all()]

    return jsonify(areas)

@app.route('/api/v1/admin/area', methods=['POST'])
@flask_login.login_required
def area_create():
    obj = Area()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/area/<int:area_id>', methods=['GET', 'PUT', 'DELETE'])
@flask_login.login_required
def area_get_update_or_delete(area_id):
    obj = Area.query.get_or_404(area_id)
    if request.method == 'GET':
        return jsonify(make_sa_row_dict(obj))

    ret = {}
    try:
        if request.method == 'PUT':
            # could validate data here...
            for k, v in request.json.iteritems():
                setattr(obj, k, v)
        else:
            db.session.delete(obj)

        db.session.commit()
    except Exception as e:
        # may fail due to FK constraints, field validation, etc
        ret['msj'] = str(e)

        return make_response(jsonify(ret), 409)

    return jsonify(ret)

# Users
@app.route('/api/v1/admin/users', methods=['GET'])
@flask_login.login_required
def user_list():
    users = []
    for user in User.query.all():
        d = make_sa_row_dict(user)
        client_name = ''
        if user.client:
            client_name = user.client.name

        d['client_name'] = client_name
        d['passwd'] = 'NONMODIFIED'

        users.append(d)

    return jsonify(users)

@app.route('/api/v1/admin/user', methods=['POST'])
@flask_login.login_required
def user_create():
    obj = User()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    errs = obj.is_valid(request.json)
    if len(errs) > 0:
        return make_response(jsonify({'validationErrors' : errs}), 409)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/user/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@flask_login.login_required
def user_get_update_or_delete(user_id):
    obj = User.query.get_or_404(user_id)
    if request.method == 'GET':
        d = make_sa_row_dict(obj)
        d['passwd'] = 'NONMODIFIED'
        return jsonify(d)

    try:
        if request.method == 'PUT':
            errs = obj.is_valid(request.json)
            if len(errs) > 0:
                return make_response(jsonify({'validationErrors' : errs}), 409)

            for k, v in request.json.iteritems():
                if k == 'passwd' and v == 'NONMODIFIED':
                    # keep the password as it is
                    continue
                setattr(obj, k, v)

        else:
            db.session.delete(obj)

        db.session.commit()
    except Exception as e:
        # may fail due to FK constraints, field validation, etc

        return make_response(jsonify({'msj' : str(e)}), 409)

    return jsonify({})

# Features
@app.route('/api/v1/admin/features', methods=['GET'])
@flask_login.login_required
def feature_list():
    features = [make_sa_row_dict(r) for r in Feature.query.all()]

    return jsonify(features)

@app.route('/api/v1/admin/feature', methods=['POST'])
@flask_login.login_required
def feature_create():
    obj = feature()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/feature/<int:feature_id>', methods=['GET', 'PUT', 'DELETE'])
@flask_login.login_required
def feature_get_update_or_delete(feature_id):
    obj = feature.query.get_or_404(feature_id)
    if request.method == 'GET':
        return jsonify(make_sa_row_dict(obj))

    ret = {}
    try:
        if request.method == 'PUT':
            # could validate data here...
            for k, v in request.json.iteritems():
                setattr(obj, k, v)
        else:
            db.session.delete(obj)

        db.session.commit()
    except Exception as e:
        # may fail due to FK constraints, field validation, etc
        ret['msj'] = str(e)

        return make_response(jsonify(ret), 409)

    return jsonify(ret)
