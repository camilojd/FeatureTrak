from featuretrak import config
config.DATABASE_URI = 'mysql://travis:@localhost/featuretrak_test'

from decimal import Decimal
from featuretrak.views import app
from featuretrak.database import db
from flask import json as JSON

# do some randomized testing
import random 

import unittest

class FeatureTrakTestCase(unittest.TestCase):
    def json_post(self, url, data):
        return self.app.post(url, data=JSON.dumps(data), content_type='application/json')

    def json_put(self, url, data):
        return self.app.put(url, data=JSON.dumps(data), content_type='application/json')

    def login_as_regular_user_sirius(self):
        return self.login_as('sirius', 'sirius123')

    def login_as_regular_user_orion(self):
        return self.login_as('orion', 'orion123')

    def login_as_admin(self):
        return self.login_as('admin', 'britec0r3')

    def login_as(self, username, passwd):
        return self.json_post('/api/v1/login', dict(username=username, passwd=passwd))

    def logout(self):
        return self.app.post('/api/v1/logout')

    def setUp(self):
        sql = '''
            INSERT INTO `areas`   VALUES (1,'Claims'),
                                         (2,'Billing'),
                                         (3,'Policies'),
                                         (4,'Reports');

            INSERT INTO `clients` VALUES (1,'Sirius Life',1.00),
                                         (2,'Orion Capital Inc.',1.00);

            INSERT INTO `users`   VALUES (1,'Administrator','admin','staff@britecore.com','britec0r3',1,NULL), 
                                         (2,'John Doe @ Sirius Life','sirius','talk@sirius.life','sirius123',0,1),
                                         (3,'Somebody @ Orion Capital','orion','ask@orion.ca','orion123',0,2);
        '''
        with app.app_context():
            db.create_all()
            db.engine.execute(sql)

        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_index(self):
        ret = self.app.get('/')
        self.assertEqual(ret.status_code, 200)

    def test_status_and_permissions_as_regular_user(self):
        # status with no session
        ret = self.app.get('/api/v1/status')
        json = JSON.loads(ret.data)
        self.assertFalse(json.has_key('username'))

        ret = self.login_as_regular_user_sirius()
        json = JSON.loads(ret.data)

        self.assertEqual(ret.status_code, 200)
        self.assertTrue(json['success'])
        self.assertFalse(json['is_admin'])

        # re-query status
        ret = self.app.get('/api/v1/status')
        json = JSON.loads(ret.data)
        self.assertTrue(json.has_key('username'))
        self.assertFalse(json['is_admin'])
        self.assertEqual(json['username'], 'sirius')
        self.assertEqual(json['full_name'], 'John Doe @ Sirius Life')

        # URL should be accesible now
        ret = self.app.get('/api/v1/features')
        self.assertEqual(ret.status_code, 200)

        # but, admin URLS don't
        # clients
        ret = self.app.get('/api/v1/admin/clients')
        self.assertEqual(ret.status_code, 403)

        ret = self.app.get('/api/v1/admin/client/1')
        self.assertEqual(ret.status_code, 403)

        ret = self.json_post('/api/v1/admin/client', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.json_put('/api/v1/admin/client/1', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.app.delete('/api/v1/admin/client/1')
        self.assertEqual(ret.status_code, 403)

        # areas
        # Only exception, to create a feature, FT needs to know the areas
        ret = self.app.get('/api/v1/admin/areas')
        self.assertEqual(ret.status_code, 200)

        ret = self.app.get('/api/v1/admin/area/1')
        self.assertEqual(ret.status_code, 403)

        ret = self.json_post('/api/v1/admin/area', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.json_put('/api/v1/admin/area/1', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.app.delete('/api/v1/admin/area/1')
        self.assertEqual(ret.status_code, 403)

        # users
        ret = self.app.get('/api/v1/admin/users')
        self.assertEqual(ret.status_code, 403)

        ret = self.app.get('/api/v1/admin/user/1')
        self.assertEqual(ret.status_code, 403)

        ret = self.json_post('/api/v1/admin/user', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.json_put('/api/v1/admin/user/1', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.app.delete('/api/v1/admin/user/1')
        self.assertEqual(ret.status_code, 403)

        # global list isn't accessible
        ret = self.app.get('/api/v1/admin/features-global')
        self.assertEqual(ret.status_code, 403)

        # create a feature should work
        ret = self.json_post('/api/v1/feature', dict(title='Some new thing',
                                                      description='Yada yada',
                                                      area_id=1))
        json = JSON.loads(ret.data)
        self.assertEqual(ret.status_code, 200)

        # modifying it, too
        ret = self.json_put('/api/v1/feature/%s' % json['id'], dict(title='Another title'))
        self.assertEqual(ret.status_code, 200)

        # deleting it, the same thing
        ret = self.app.delete('/api/v1/feature/%s' % json['id'])
        self.assertEqual(ret.status_code, 200)

        ret = self.logout()
        self.assertEqual(ret.status_code, 200)

        # logged out, now this won't be authorized
        ret = self.app.get('/api/v1/features')
        self.assertEqual(ret.status_code, 403)

    def test_admin_clients(self):
        # test admin URLs when there's no session
        ret = self.app.get('/api/v1/admin/clients')
        self.assertEqual(ret.status_code, 403)

        ret = self.app.get('/api/v1/admin/client/1')
        self.assertEqual(ret.status_code, 403)

        ret = self.json_post('/api/v1/admin/client', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.json_put('/api/v1/admin/client/1', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.app.delete('/api/v1/admin/client/1')
        self.assertEqual(ret.status_code, 403)

        # now, login and perform admin actions
        ret = self.login_as_admin()
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)

        self.assertEqual(ret.status_code, 200)
        self.assertTrue(json['success'])
        self.assertTrue(json['is_admin'])

        # see if we have all initially loaded clients
        ret = self.app.get('/api/v1/admin/clients')
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(len(json), 2)

        # query one known client
        ret = self.app.get('/api/v1/admin/client/1')
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)

        self.assertEqual(json['name'], 'Sirius Life')

        # create another
        ret = self.json_post('/api/v1/admin/client', dict(name='Lindy Mutual'))
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        client_id = json['id']

        # verify it's there
        ret = self.app.get('/api/v1/admin/client/%s' % client_id)
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(json['name'], 'Lindy Mutual')

        # alter the name and weight
        weight = Decimal( str((random.random() * 9) + 1.1) ).quantize(Decimal('0.01'))
        name = random.choice(['Lindy Corporate', 'Lindy Health Co.', 'Lindy Insurance'])

        ret = self.json_put('/api/v1/admin/client/%s' % client_id,
                             dict(name=name,
                                  weight=str(weight)))

        self.assertEqual(ret.status_code, 200)

        # verify modification
        ret = self.app.get('/api/v1/admin/client/%s' % client_id)
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(json['name'], name)
        self.assertEqual(json['weight'], str(weight))

        ret = self.app.delete('/api/v1/admin/client/%s' % client_id)
        self.assertEqual(ret.status_code, 200)

        ret = self.logout()
        self.assertEqual(ret.status_code, 200)

    def test_admin_areas(self):
        # test admin URLs when there's no session
        ret = self.app.get('/api/v1/admin/areas')
        self.assertEqual(ret.status_code, 403)

        ret = self.app.get('/api/v1/admin/area/1')
        self.assertEqual(ret.status_code, 403)

        ret = self.json_post('/api/v1/admin/area', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.json_put('/api/v1/admin/area/1', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.app.delete('/api/v1/admin/area/1')
        self.assertEqual(ret.status_code, 403)

        # now, login and perform admin actions
        ret = self.login_as_admin()
        self.assertEqual(ret.status_code, 200)

        # see if we have all initially loaded areas
        ret = self.app.get('/api/v1/admin/areas')
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(len(json), 4)

        # query one known area
        ret = self.app.get('/api/v1/admin/area/3')
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)

        self.assertEqual(json['name'], 'Policies')

        # create another
        ret = self.json_post('/api/v1/admin/area', dict(name='Compliance'))
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        area_id = json['id']

        # verify it's there
        ret = self.app.get('/api/v1/admin/area/%s' % area_id)
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(json['name'], 'Compliance')

        # alter the name
        ret = self.json_put('/api/v1/admin/area/%s' % area_id, dict(name='Analytics'))

        self.assertEqual(ret.status_code, 200)

        # verify modification
        ret = self.app.get('/api/v1/admin/area/%s' % area_id)
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(json['name'], 'Analytics')

        ret = self.app.delete('/api/v1/admin/area/%s' % area_id)
        self.assertEqual(ret.status_code, 200)

        ret = self.logout()
        self.assertEqual(ret.status_code, 200)

    def test_admin_users(self):
        # test admin URLs when there's no session
        ret = self.app.get('/api/v1/admin/users')
        self.assertEqual(ret.status_code, 403)

        ret = self.app.get('/api/v1/admin/user/1')
        self.assertEqual(ret.status_code, 403)

        ret = self.json_post('/api/v1/admin/user', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.json_put('/api/v1/admin/user/1', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.app.delete('/api/v1/admin/user/1')
        self.assertEqual(ret.status_code, 403)

        # now, login and perform admin actions
        ret = self.login_as_admin()
        self.assertEqual(ret.status_code, 200)

        # see if we have all initially loaded users
        ret = self.app.get('/api/v1/admin/users')
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(len(json), 3)

        # query one known user
        ret = self.app.get('/api/v1/admin/user/3')
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)

        self.assertEqual(json['username'], 'orion')
        self.assertEqual(json['full_name'], 'Somebody @ Orion Capital')
        self.assertEqual(json['email'], 'ask@orion.ca')

        # create another
        ret = self.json_post('/api/v1/admin/user',
                              dict(username='ender',
                                   full_name='Ender Wiggin',
                                   email='ender@exile.os',
                                   passwd='qazwsx',
                                   is_admin=False,
                                   client_id=2))

        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        user_id = json['id']

        # verify it's there
        ret = self.app.get('/api/v1/admin/user/%s' % user_id)
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(json['username'], 'ender')
        self.assertEqual(json['full_name'], 'Ender Wiggin')
        self.assertEqual(json['email'], 'ender@exile.os')

        # alter the email
        ret = self.json_put('/api/v1/admin/user/%s' % user_id, dict(email='outer@space'))

        self.assertEqual(ret.status_code, 200)

        # verify modification
        ret = self.app.get('/api/v1/admin/user/%s' % user_id)
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(json['username'], 'ender')
        self.assertEqual(json['full_name'], 'Ender Wiggin')
        self.assertEqual(json['email'], 'outer@space')

        # now, logout and try to login as the new user
        ret = self.logout()
        self.assertEqual(ret.status_code, 200)

        ret = self.login_as('ender', 'qazwsx')
        self.assertEqual(ret.status_code, 200)

        # verify status session
        ret = self.app.get('/api/v1/status')
        json = JSON.loads(ret.data)
        self.assertTrue(json.has_key('username'))
        self.assertEqual(json['username'], 'ender')

        ret = self.logout()
        self.assertEqual(ret.status_code, 200)

        # back to admin user
        ret = self.login_as_admin()
        self.assertEqual(ret.status_code, 200)

        # finally delete the user
        ret = self.app.delete('/api/v1/admin/user/%s' % user_id)
        self.assertEqual(ret.status_code, 200)

        ret = self.logout()
        self.assertEqual(ret.status_code, 200)

    def test_feature_creation_and_prioritization(self):
        # test URLs when there's no session
        ret = self.app.get('/api/v1/features')
        self.assertEqual(ret.status_code, 403)

        ret = self.app.get('/api/v1/feature/1')
        self.assertEqual(ret.status_code, 403)

        ret = self.json_post('/api/v1/feature', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.json_put('/api/v1/feature/1', dict(some='value'))
        self.assertEqual(ret.status_code, 403)

        ret = self.app.delete('/api/v1/feature/1')
        self.assertEqual(ret.status_code, 403)

        # now, login
        self.login_as_regular_user_sirius()

        ret = self.app.get('/api/v1/features')
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)
        self.assertEqual(len(json['own']), 0)
        self.assertEqual(len(json['others']), 0)

        # create 3 features
        for feat in range(1, 4):
            ret = self.json_post('/api/v1/feature',
                                 dict(title='Feature %s' % feat,
                                      description='Yada yada',
                                      area_id=random.choice([1, 2, 3, 4]),
                                      is_public=False))
            self.assertEqual(ret.status_code, 200)

        ret = self.app.get('/api/v1/features')
        json = JSON.loads(ret.data)
        self.assertEqual(len(json['own']), 3)
        self.assertEqual(len(json['others']), 0)

        # shouldn't be able to see global ranking as regular user
        ret = self.app.get('/api/v1/admin/features-global')
        self.assertEqual(ret.status_code, 403)

        self.logout()

        # verify as admin the order of created features
        self.login_as_admin()

        ret = self.app.get('/api/v1/admin/features-global')
        json = JSON.loads(ret.data)

        self.assertEqual(json[0]['id'], 1)
        self.assertEqual(json[0]['title'], 'Feature 1')

        self.assertEqual(json[1]['id'], 2)
        self.assertEqual(json[1]['title'], 'Feature 2')

        self.assertEqual(json[2]['id'], 3)
        self.assertEqual(json[2]['title'], 'Feature 3')

        self.logout()

        self.login_as_regular_user_sirius()
        
        ret = self.json_post('/api/v1/sort-features',
                             dict(features=[2, 3, 1]))

        # check client "private order"
        ret = self.app.get('/api/v1/features')
        json = JSON.loads(ret.data)

        self.assertEqual(json['own'][0]['id'], 2)
        self.assertEqual(json['own'][1]['id'], 3)
        self.assertEqual(json['own'][2]['id'], 1)

        self.logout()

        self.login_as_admin()

        ret = self.app.get('/api/v1/admin/features-global')
        json = JSON.loads(ret.data)

        # global order should be consistent w/ unique client order
        self.assertEqual(json[0]['id'], 2)
        self.assertEqual(json[1]['id'], 3)
        self.assertEqual(json[2]['id'], 1)

        self.logout()

        self.login_as_regular_user_orion()

        # now, create a new feature using Orion which doesn't have any
        ret = self.json_post('/api/v1/feature',
                             dict(title='Feature from Orion',
                                  description='Some interesting detail',
                                  area_id=random.choice([1, 2, 3, 4]),
                                  is_public=False))
        self.logout()

        self.login_as_admin()

        # re-check global priorities
        ret = self.app.get('/api/v1/admin/features-global')
        json = JSON.loads(ret.data)

        # Sirius still top because it was created earlier
        self.assertEqual(json[0]['id'], 2)
        self.assertEqual(json[1]['id'], 4)
        self.assertEqual(json[2]['id'], 3)
        self.assertEqual(json[3]['id'], 1)

        # alter Orion's weight so it's unique feature will rise to the top
        self.json_put('/api/v1/admin/client/2', dict(weight='1.2'))

        ret = self.app.get('/api/v1/admin/features-global')
        json = JSON.loads(ret.data)

        self.assertEqual(json[0]['id'], 4)
        self.assertEqual(json[1]['id'], 2)
        self.assertEqual(json[2]['id'], 3)
        self.assertEqual(json[3]['id'], 1)

        self.logout()
    def test_public_feature(self):
        self.login_as_regular_user_sirius()

        ret = self.json_post('/api/v1/feature',
                             dict(title='Special snowflake feature',
                                  description='Yada yada',
                                  area_id=random.choice([1, 2, 3, 4]),
                                  is_public=True))

        # check client "private order"
        ret = self.app.get('/api/v1/features')
        self.assertEqual(ret.status_code, 200)
        json = JSON.loads(ret.data)

        self.assertEqual(len(json['own']), 1)
        self.assertEqual(len(json['others']), 0)
        self.assertEqual(json['own'][0]['id'], 1)

        self.logout()

        # public feature should be visible to orion
        self.login_as_regular_user_orion()

        ret = self.app.get('/api/v1/features')
        json = JSON.loads(ret.data)

        self.assertEqual(len(json['own']), 0)
        self.assertEqual(len(json['others']), 1)
        self.assertEqual(json['others'][0]['id'], 1)

        # orion decides to back this feature
        ret = self.json_post('/api/v1/sort-features', dict(features=[1]))
        self.assertEqual(ret.status_code, 200)

        ret = self.app.get('/api/v1/features')
        json = JSON.loads(ret.data)

        self.assertEqual(len(json['own']), 1)
        self.assertEqual(len(json['others']), 1)
        self.assertEqual(json['own'][0]['id'], 1)
        self.assertEqual(json['others'][0]['id'], 1)

        self.logout()

        self.login_as_admin()

        # the same unique feature backed by two clients (creator + supporter) should have a rank of 2.000
        ret = self.app.get('/api/v1/admin/features-global')
        json = JSON.loads(ret.data)

        self.assertEqual(json[0]['id'], 1)
        self.assertEqual(json[0]['rank'], '2.000')

        self.logout()

        self.login_as_regular_user_sirius()

        # sirius can't edit its public feature because orion is backing it
        ret = self.json_put('/api/v1/feature/1', dict(title='Another title'))
        self.assertEqual(ret.status_code, 409)
        json = JSON.loads(ret.data)

        self.assertEqual(json['msgType'], 'error')
        self.assertEqual(json['msgText'], 
                         "Unable to edit or delete public feature, it's currently supported by other clients")

        # sirius can't delete its public feature because orion is backing it
        ret = self.app.delete('/api/v1/feature/1')
        self.assertEqual(ret.status_code, 409)
        json = JSON.loads(ret.data)

        self.assertEqual(json['msgType'], 'error')
        self.assertEqual(json['msgText'], 
                         "Unable to edit or delete public feature, it's currently supported by other clients")
        
        self.logout()

        self.login_as_regular_user_orion()

        # stop backing the feature
        ret = self.json_post('/api/v1/sort-features', dict(features=[]))
        self.assertEqual(ret.status_code, 200)

        self.logout()

        self.login_as_regular_user_sirius()

        # now sirius can delete the feature
        ret = self.app.delete('/api/v1/feature/1')
        self.assertEqual(ret.status_code, 200)

        ret = self.app.get('/api/v1/features')
        json = JSON.loads(ret.data)

        self.assertEqual(len(json['own']), 0)
        self.assertEqual(len(json['others']), 0)

        self.logout()

if __name__ == '__main__':
    unittest.main()
