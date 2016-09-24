from featuretrak import app, db
from featuretrak.models import User, Area, Client
import datetime as dt
import os
import sys

if not os.environ.has_key('FEATURETRAK_CONFIG'):
    print "The environment var FEATURETRAK_CONFIG needs to be set to populate the database"
    sys.exit(1)

app.app_context().push()
db.drop_all()
db.create_all()

area_policies = Area()
area_policies.name = 'Policies'

area_billing = Area()
area_billing.name = 'Billing'

area_claims = Area()
area_claims.name = 'Claims'

area_reports = Area()
area_reports.name = 'Reports'

client_proxima = Client()
client_proxima.name = 'Proxima Insurance'
client_proxima.weight = 1

user_admin = User()
user_admin.username = 'admin'
user_admin.full_name = 'Administrator'
user_admin.is_admin = True
user_admin.email = 'staff@britecore.com'
user_admin.passwd = 'britecore' #nope, not using bcrypt (yet)
user_admin.is_enabled = True

db.session.add(area_policies)
db.session.add(area_billing)
db.session.add(area_claims)
db.session.add(area_reports)
db.session.add(client_proxima)
db.session.add(user_admin)

db.session.commit()
