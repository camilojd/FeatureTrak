# defaults

DATABASE_URI = ''
GOOGLE_CLIENT_ID = ''
FLASK_SECRET_KEY = ''
DEBUG = False

try:
    from config_local import *
except:
    pass
