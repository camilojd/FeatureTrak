from featuretrak.database import app, db, User, Feature, Client, Area
import datetime as dt

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

client_draco = Client()
client_draco.name = 'Draco Mutual'
client_draco.weight = 1

client_orion = Client()
client_orion.name = 'Orion Capital Inc.'
client_orion.weight = 1

client_talitha = Client()
client_talitha.name = 'Talitha Property'
client_talitha.weight = 1

client_gemma = Client()
client_gemma.name = 'Gemma Casualty'
client_gemma.weight = 1

req = Feature()
req.title = 'Avoid collapsing notification window'
req.description = 'Whenever someone clicks onto bla bla bla...'
req.target_date = dt.date.today()
req.url = 'https://www.google.com'
req.client = client_sirius
req.area = area_claims

user_admin = User()
user_admin.username = 'admin'
user_admin.full_name = 'Administrator'
user_admin.is_admin = True
user_admin.email = 'staff@britecore.com'
user_admin.passwd = '$$'

user_talitha = User()
user_talitha.username = 'talitha'
user_talitha.full_name = 'Somebody @ Talitha Property'
user_talitha.is_admin = False
user_talitha.email = 'ask@talitha.prop'
user_talitha.passwd = '$$'
user_talitha.client = client_talitha

db.session.add(req)
db.session.add(area_policies)
db.session.add(area_billing)
db.session.add(area_reports)
db.session.add(client_proxima)
db.session.add(client_draco)
db.session.add(client_orion)
db.session.add(client_talitha)
db.session.add(client_gemma)
db.session.add(user_admin)
db.session.add(user_talitha)

db.session.commit()

