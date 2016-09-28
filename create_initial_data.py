from featuretrak import app, db
from featuretrak.models import User, Area, Client
import datetime as dt
import os
import sys

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

client_sirius = Client()
client_sirius.name = 'Sirius Life'
client_sirius.weight = 1

user_admin = User()
user_admin.username = 'admin'
user_admin.full_name = 'Administrator'
user_admin.is_admin = True
user_admin.email = 'staff@britecore.com'
user_admin.passwd = 'britecore'
user_admin.is_enabled = True

user_proxima = User()
user_proxima.username = 'proxima'
user_proxima.full_name = 'Jane Doe @ Proxima Insurance'
user_proxima.is_admin = False
user_proxima.email = 'ask@proxima.com'
user_proxima.passwd = 'proxima'
user_proxima.client = client_proxima
user_proxima.is_enabled = True

user_sirius = User()
user_sirius.username = 'sirius'
user_sirius.full_name = 'John Doe @ Sirius Life'
user_sirius.is_admin = False
user_sirius.email = 'sirius@li.fe'
user_sirius.passwd = 'sirius'
user_sirius.client = client_sirius
user_sirius.is_enabled = True

db.session.add(area_policies)
db.session.add(area_billing)
db.session.add(area_claims)
db.session.add(area_reports)

db.session.add(client_proxima)
db.session.add(client_sirius)

db.session.add(user_admin)
db.session.add(user_proxima)
db.session.add(user_sirius)

db.session.commit()
