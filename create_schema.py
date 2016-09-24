from featuretrak import app, db
from featuretrak.models import User, Feature, Client, Area, Supporter
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

# Features
# Sirius - 1st private feature

feature = Feature()
feature.title = '''
Support the before option on binding handlers 
'''.strip()
feature.description = '''
Currently there is no nice way to define a custom binding handler, which has to execute before other bindings. The only way I see is to modify every related binding handler and add the custom binding to their after array.

Using a before array would result a much nicer and more readable syntax.

Now

ko.bindingHandlers.sampleBinding = {
  init: ...  
}
ko.bindingHandlers.value.after = (ko.bindingHandlers.value.after || []).concat(["sampleBinding"]);
ko.bindingHandlers.checked.after =(ko.bindingHandlers.checked.after || []).concat(["sampleBinding"]);
ko.bindingHandlers.options.after = (ko.bindingHandlers.options.after || []).concat(["sampleBinding"]);
Proposed solution

ko.bindingHandlers.sampleBinding = {
  before: ["value", "checked", "options"],
  init: ...  
}
'''.strip()
feature.target_date = dt.date.today()
feature.url = 'https://www.google.com'
feature.client = client_sirius
feature.area = area_claims
feature.is_public = False

supporter = Supporter()
supporter.feature = feature
supporter.client = client_sirius
supporter.priority = 0

db.session.add(feature)
db.session.add(supporter)

# Sirius - 2nd private feature

feature = Feature()
feature.title = '''
Provide a way to get all bindings in a binding handler
'''.strip()
feature.description = '''
I see in the source code that it's possible to call allBindings as a function and it will return an object with all binding keys and their appropriate value accessors. However I also see the note that this kind of usage is deprecated.

The current version exposes only a get and a has function, and they both operate with a concrete binding key as a parameter. So basically there is no chance to get all bindings except using the deprecated function call.

First I'd like to ask why it was deprecated. Was there any kind of technical issue, or performance problem, or anything? Or was it just an API change so that using it in most cases got nicer and simpler?

If there are no technical limitations, it would be good to either have an all function on allBindings, or modify get to be able to call it without parameter, and in that case it would return all bindings.
'''.strip()
feature.target_date = dt.date.today()
feature.url = 'https://www.google.com'
feature.client = client_sirius
feature.area = area_billing
feature.is_public = False

supporter = Supporter()
supporter.feature = feature
supporter.client = client_sirius
supporter.priority = 1

db.session.add(feature)
db.session.add(supporter)

# Sirius - unique 'public' feature

feature = Feature()
feature.title = '''
ft - template engine helper for version 3.5.0
'''.strip()
feature.description = '''
I recently using this feature on an expiremental durandal project and maybe someone find this helpful to knockoutjs.
In durandal, the function is inserted on viewEngine.js on line and the to convert all new bindings and the code became like this:

var newMarkup = templateEngineHelper(markup); //`markup` is the html node in string
var element = that.processMarkup(newMarkup);
'''.strip()
feature.target_date = dt.date.today()
feature.url = 'https://www.google.com'
feature.client = client_sirius
feature.area = area_billing
feature.is_public = True

supporter = Supporter()
supporter.feature = feature
supporter.client = client_sirius
supporter.priority = 2

db.session.add(feature)
db.session.add(supporter)

# Orion - 1st feature - private

feature = Feature()
feature.title = '''
IE 11 - KO performance with our application is 5~10 times slower than Chrome.
'''.strip()
feature.description = '''
Knockout for our application has a very good performance result with Chrome however it's 5~10 times slower in IE 11 even crashed. Does anyone have encountered it or any solution or workaround? Thanks in advance.
'''.strip()
feature.target_date = dt.date.today()
feature.url = 'https://www.google.com'
feature.client = client_orion
feature.area = area_policies
feature.is_public = False

supporter = Supporter()
supporter.feature = feature
supporter.client = client_orion
supporter.priority = 0

db.session.add(feature)
db.session.add(supporter)

# Orion - 2nd feature - private

feature = Feature()
feature.title = '''
return component's viewmodel after applyBindings?
'''.strip()
feature.description = '''
var vm = ko.applyBindings({}, elem);
This would be handy because I can easily call the functions inside of component's view model.

For example,

window.showMsg = vm.show
'''.strip()
feature.target_date = dt.date.today()
feature.url = 'https://www.google.com'
feature.client = client_orion
feature.area = area_policies
feature.is_public = False

supporter = Supporter()
supporter.feature = feature
supporter.client = client_orion
supporter.priority = 1

db.session.add(feature)
db.session.add(supporter)

# Users

user_admin = User()
user_admin.username = 'admin'
user_admin.full_name = 'Administrator'
user_admin.is_admin = True
user_admin.email = 'staff@britecore.com'
user_admin.passwd = 'britec0r3' #nope, not using bcrypt (yet)
user_admin.is_enabled = True

user_orion = User()
user_orion.username = 'orion'
user_orion.full_name = 'Somebody @ Orion Capital'
user_orion.is_admin = False
user_orion.email = 'ask@orion.ca'
user_orion.passwd = 'orion123'
user_orion.client = client_orion
user_orion.is_enabled = True

user_sirius = User()
user_sirius.username = 'sirius'
user_sirius.full_name = 'John Doe @ Sirius Life'
user_sirius.is_admin = False
user_sirius.email = 'sirius@li.fe'
user_sirius.passwd = 'sirius123'
user_sirius.client = client_sirius
user_sirius.is_enabled = True

db.session.add(area_policies)
db.session.add(area_billing)
db.session.add(area_reports)
db.session.add(client_proxima)
db.session.add(client_draco)
db.session.add(client_orion)
db.session.add(client_talitha)
db.session.add(client_gemma)
db.session.add(user_admin)
db.session.add(user_orion)
db.session.add(user_sirius)

db.session.commit()

