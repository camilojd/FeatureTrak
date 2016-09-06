from featuretrak.database import create_app, db, User, Feature, Client, Area
import datetime as dt

app = create_app()
app.app_context().push()
db.drop_all()
db.create_all()

area_policies = Area('Policies')
area_billing = Area('Billing')
area_claims = Area('Claims')
area_reports = Area('Reports')

client_proxima = Client('Proxima Insurance')

client_sirius = Client('Sirius Life')
req = Feature('Avoid collapsing notification window',
              'Whenever someone clicks onto bla bla bla...',
              dt.date.today(), 'https://www.google.com')
req.client = client_sirius
req.area = area_claims

db.session.add(req)
db.session.add(area_policies)
db.session.add(area_billing)
db.session.add(area_reports)
db.session.add(client_proxima)

db.session.commit()

