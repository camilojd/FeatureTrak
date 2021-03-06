from featuretrak import app
from flask import render_template, jsonify, request, make_response, abort
from models import db, User, Client, Area, Feature, Supporter
from decimal import Decimal
from sqlalchemy import and_, func
import flask_login

# helper
def make_sa_row_dict(obj):
    d = dict(obj.__dict__)
    d.pop('_sa_instance_state', None)
    return d

# main view
@app.route('/')
def index():
    return render_template('base.html',
                           GOOGLE_CLIENT_ID=app.config['GOOGLE_CLIENT_ID'])

@app.route('/api/v1/status')
def status():
    user = flask_login.current_user
    status = {}
    if user.is_authenticated:
        status['username'] = user.username
        status['full_name'] = user.full_name
        status['is_admin'] = user.is_admin
        status['is_enabled'] = user.is_enabled
        status['client_id'] = user.client_id
        status['success'] = True

    return jsonify(status)

@app.route('/api/v1/login', methods=['POST'])
def login():
    criteria = {'google_id' : None}
    if '@' in request.json['username']:
        criteria['email'] = request.json['username']
    else:
        criteria['username'] = request.json['username']

    user = User.query.filter_by(**criteria).first() 

    if user is not None and user.passwd == request.json['passwd']:
        # not using bcrypt (yet)
        flask_login.login_user(user)
        return jsonify({'success' : True, 'is_admin' : user.is_admin, 'client_id' : user.client_id,
                        'full_name' : user.full_name, 'username' : user.username,
                        'is_enabled' : user.is_enabled})

    return jsonify({'success': False, 'msgText': 'Invalid credentials', 'msgType': 'error'})

@app.route('/api/v1/google-login', methods=['POST'])
def google_login():
    from oauth2client import client, crypt

    try:
        idinfo = client.verify_id_token(request.json['token'], app.config['GOOGLE_CLIENT_ID'])
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
    except crypt.AppIdentityError:
        # Invalid token
        return jsonify(dict(success=False))

    userid = idinfo['sub']

    user = User.query.filter(User.google_id == userid).first()

    if user is None:
        user = User()
        user.username = 'goog_%s' % userid
        user.full_name = idinfo['name']
        user.email = idinfo['email']
        user.google_id = userid
        user.is_admin = False
        user.is_enabled = False

        db.session.add(user)
        db.session.commit()

    flask_login.login_user(user)

    ret = {}
    ret['success'] = True
    ret['username'] = user.username
    ret['full_name'] = user.full_name
    ret['client_id'] = user.client_id
    ret['is_admin'] = user.is_admin
    ret['is_enabled'] = user.is_enabled

    return jsonify(ret)

@app.route('/api/v1/confirm-user-client', methods=['POST'])
@flask_login.login_required
def assign_user_client():
    if flask_login.current_user.is_enabled:
        # once assigned can't be reassigned
        abort(400)

    user = User.query.get(flask_login.current_user.id)
    user.client_id = request.json['client_id']
    user.is_enabled = True

    db.session.commit()

    return jsonify(dict(success=True))

@app.route('/api/v1/logout', methods=['POST'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return jsonify({'success' : True})

# API views
# Clients
@app.route('/api/v1/admin/clients', methods=['GET'])
@flask_login.login_required
def client_list():
    clients = [r.to_dict() for r in Client.query.all()]

    return jsonify(clients)

@app.route('/api/v1/admin/client', methods=['POST'])
@flask_login.login_required
def client_create():
    if not flask_login.current_user.is_admin:
        abort(403)

    obj = Client()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    errs = obj.is_valid(request.json)
    if len(errs) > 0:
        return make_response(jsonify({'validationErrors' : errs}), 409)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/client/<int:client_id>', methods=['GET', 'PUT', 'DELETE'])
@flask_login.login_required
def client_get_update_or_delete(client_id):
    if not flask_login.current_user.is_admin:
        abort(403)

    obj = Client.query.get_or_404(client_id)
    if request.method == 'GET':
        return jsonify(obj.to_dict())

    ret = {}
    try:
        if request.method == 'PUT':
            for k, v in request.json.iteritems():
                setattr(obj, k, v)

            errs = obj.is_valid(request.json)
            if len(errs) > 0:
                return make_response(jsonify({'validationErrors' : errs}), 409)

        else:
            db.session.delete(obj)

        db.session.commit()
    except Exception as e:
        # may fail due to FK constraints, field validation, etc
        ret['msgText'] = 'Exception: ' + str(e)
        ret['msgType'] = 'error'

        return make_response(jsonify(ret), 409)

    return jsonify(ret)

# Areas
@app.route('/api/v1/admin/areas', methods=['GET'])
@flask_login.login_required
def area_list():
    # all users can query this
    areas = [make_sa_row_dict(r) for r in Area.query.all()]

    return jsonify(areas)

@app.route('/api/v1/admin/area', methods=['POST'])
@flask_login.login_required
def area_create():
    if not flask_login.current_user.is_admin:
        abort(403)

    obj = Area()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/area/<int:area_id>', methods=['GET', 'PUT', 'DELETE'])
@flask_login.login_required
def area_get_update_or_delete(area_id):
    if not flask_login.current_user.is_admin:
        abort(403)

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
        ret['msgText'] = 'Exception: ' + str(e)
        ret['msgType'] = 'error'

        return make_response(jsonify(ret), 409)

    return jsonify(ret)

# Users
@app.route('/api/v1/admin/users', methods=['GET'])
@flask_login.login_required
def user_list():
    if not flask_login.current_user.is_admin:
        abort(403)

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
    if not flask_login.current_user.is_admin:
        abort(403)

    obj = User()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    errs = obj.is_valid(request.json)
    if len(errs) > 0:
        return make_response(jsonify({'validationErrors' : errs}), 409)

    # users created by API/Web UI are enabled by default
    obj.is_enabled = True

    db.session.add(obj)
    db.session.commit()

    return jsonify({'id': obj.id})

@app.route('/api/v1/admin/user/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@flask_login.login_required
def user_get_update_or_delete(user_id):
    if not flask_login.current_user.is_admin:
        abort(403)

    obj = User.query.get_or_404(user_id)
    if request.method == 'GET':
        d = make_sa_row_dict(obj)
        d['passwd'] = 'NONMODIFIED'
        return jsonify(d)

    ret = {}

    try:
        if request.method == 'PUT':
            for k, v in request.json.iteritems():
                if k == 'passwd' and v == 'NONMODIFIED':
                    # keep the password as it is
                    continue
                setattr(obj, k, v)

            if obj.is_admin:
                # to match the UI
                obj.client_id = None

            errs = obj.is_valid(request.json)
            if len(errs) > 0:
                return make_response(jsonify({'validationErrors' : errs}), 409)

        else:
            db.session.delete(obj)

        db.session.commit()
    except Exception as e:
        # may fail due to FK constraints, field validation, etc
        ret['msgText'] = 'Exception: ' + str(e)
        ret['msgType'] = 'error'

        return make_response(jsonify(ret), 409)

    return jsonify(ret)

# Features
@app.route('/api/v1/features', methods=['GET'])
@flask_login.login_required
def feature_list():
    if not flask_login.current_user.is_enabled:
        abort(403)

    user = flask_login.current_user

    own_features = []
    public_supported = {}
    for feature in Feature.query.join(Feature.supporters) \
                                 .filter(Supporter.client_id == user.client_id) \
                                 .order_by(Supporter.priority):
        row = feature.to_dict()
        # is this feature a public one that belongs to another client?
        row['belongs_to_another'] = user.client_id != feature.client.id
        if row['belongs_to_another']:
            public_supported[feature.id] = 1
        own_features.append(row)

    others_public_features = []
    for feature in Feature.query.filter(and_(Feature.client_id != user.client_id,
                                             Feature.is_public == True)):
        row = feature.to_dict()
        row['included'] = public_supported.has_key(feature.id)
        others_public_features.append(row)

    return jsonify({'own' : own_features, 'others' : others_public_features})

@app.route('/api/v1/feature', methods=['POST'])
@flask_login.login_required
def feature_create():
    if not flask_login.current_user.is_enabled:
        abort(403)

    obj = Feature()
    for k, v in request.json.iteritems():
        setattr(obj, k, v)

    if obj.area_id is None:
        return make_response(jsonify({'validationErrors' : ['An area should be specified']}), 409)

    user = flask_login.current_user
    obj.client_id = user.client.id
    db.session.add(obj)

    # associate as Supporter
    max_priority = db.session.query(func.max(Supporter.priority)) \
                             .filter(Supporter.client_id == user.client.id).first()
    supporter = Supporter()
    supporter.client_id = user.client.id
    supporter.feature_id = obj.id
    supporter.priority = 0 if max_priority[0] is None else (max_priority[0] + 1)
    db.session.add(supporter)

    db.session.commit()

    return jsonify({'id': obj.id, 'msgType': 'info', 'msgText': 'Feature created'})

@app.route('/api/v1/feature/<int:feature_id>', methods=['GET', 'PUT', 'DELETE'])
@flask_login.login_required
def feature_get_update_or_delete(feature_id):
    if not flask_login.current_user.is_enabled:
        abort(403)

    obj = Feature.query.get_or_404(feature_id)
    if request.method == 'GET':
        return jsonify(obj.to_dict())

    ret = {}
    try:
        if obj.is_public:
            # public features currently backed by other clients cannot be edited nor deleted
            user = flask_login.current_user
            others_cnt = Supporter.query.filter(and_(Supporter.client_id != user.client.id,
                                                     Supporter.feature_id == obj.id)).count()
            if others_cnt > 0:
                ret['msgText'] = "Unable to edit or delete public feature, it's currently supported by other clients"
                ret['msgType'] = 'error'
                return make_response(jsonify(ret), 409)

        if request.method == 'PUT':
            # could validate data here...
            for k, v in request.json.iteritems():
                setattr(obj, k, v)
        else:
            Supporter.query.filter(Supporter.feature_id == obj.id).delete()
            db.session.delete(obj)

        db.session.commit()
    except Exception as e:
        # may fail due to FK constraints, field validation, etc
        ret['msgText'] = 'Exception: ' + str(e)
        ret['msgType'] = 'error'

        return make_response(jsonify(ret), 409)

    return jsonify(ret)

@app.route('/api/v1/sort-features', methods=['POST'])
@flask_login.login_required
def feature_sort():
    if not flask_login.current_user.is_enabled:
        abort(403)

    # TODO validate that only public features or features belonging
    # to this user can be sorted
    user = flask_login.current_user
    Supporter.query.filter(Supporter.client_id == user.client_id).delete()
    priority = 0
    for feature_id in request.json['features']:
        supporter = Supporter()
        supporter.feature_id = feature_id
        supporter.client_id = user.client.id
        supporter.priority = priority
        priority += 1
        db.session.add(supporter)

    db.session.commit()

    return jsonify({'ret' : True, 'msgType' : 'info', 'msgText': 'Priority order updated'})


@app.route('/api/v1/admin/features-global', methods=['GET'])
@flask_login.login_required
def features_global_list():
    if not flask_login.current_user.is_admin:
        abort(403)

    sql = '''
        select a.feature_id,
               sum(a.points) as rank
          from ( select s.feature_id,
                        ((summary.cnt - s.priority - summary.min_priority) / summary.cnt) * c.weight  as points
                   from supporters s
                        inner join (select client_id,
                                           min(priority) as min_priority,
                                           count(*) as cnt
                                      from supporters
                                     group by client_id) summary on (s.client_id = summary.client_id)
                        inner join clients c on (s.client_id = c.id)) a
         group by a.feature_id
        order by rank desc, feature_id asc -- tie break on first created
    '''

    quantize_factor = Decimal('0.001')
    features = []
    for row in db.engine.execute(sql):
        feature_row = Feature.query.get(row[0]).to_dict(include_supporters=True)
        feature_row['rank'] = str(row[1].quantize(quantize_factor))
        features.append(feature_row)

    return jsonify(features)
