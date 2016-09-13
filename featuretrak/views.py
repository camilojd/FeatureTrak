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

@app.route('/logmein')
def logmein():
    my_user = User.query.get(1)
    flask_login.login_user(my_user)
    return 'ya esta....'

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'desloggeado....'

@app.route('/whoami')
@flask_login.login_required
def whoami():
    return '{}'.format(flask_login.current_user.full_name)

@app.route('/test')
def my_test():
    return make_response(jsonify([2,3,5,8,13]), 409)

# API views
# TODO add credentials validation for admin site

# Clients
@app.route('/api/v1/admin/clients', methods=['GET'])
def client_list():
    clients = [make_sa_row_dict(r) for r in Client.query.all()]

    return jsonify(clients)

@app.route('/api/v1/admin/client', methods=['POST'])
def client_create():
    obj = Client()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/client/<int:client_id>', methods=['GET', 'PUT', 'DELETE'])
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
def area_list():
    areas = [make_sa_row_dict(r) for r in Area.query.all()]

    return jsonify(areas)

@app.route('/api/v1/admin/area', methods=['POST'])
def area_create():
    obj = Area()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/area/<int:area_id>', methods=['GET', 'PUT', 'DELETE'])
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
def user_create():
    obj = User()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/user/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_get_update_or_delete(user_id):
    obj = User.query.get_or_404(user_id)
    if request.method == 'GET':
        d = make_sa_row_dict(obj)
        d['passwd'] = 'NONMODIFIED'
        return jsonify(d)

    ret = {}
    try:
        if request.method == 'PUT':
            if 'is_admin' in request.json:
                # admins don't belong to a client, non admins should always belong to one
                if request.json['is_admin'] is True:
                    obj.client_id = None
                else:
                    if not request.json.has_key('client_id'):
                        ret['validationErrors'] = ['User should be assigned to a client']
                        return make_response(jsonify(ret), 409)

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
        ret['msj'] = str(e)

        return make_response(jsonify(ret), 409)

    return jsonify(ret)
