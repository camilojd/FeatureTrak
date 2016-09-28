from PyWebRunner import WebTester
import unittest

class Test(unittest.TestCase):
    def assert_text_in_elements(self, selector, text):
        # WebRunner has problems with unicode because uses str()
        html_text = ''.join([e.text for e in self.wt.get_elements(selector)])
        self.assertTrue(text in html_text)

    @classmethod
    def setUpClass(cls):
        cls.wt = WebTester()
        cls.wt.start()

    @classmethod
    def tearDownClass(cls):
        cls.wt.stop()

    def test_login_invalid_shows_notification(self):
        self.wt.go('http://localhost:5000/')

        self.wt.wait_for_visible('#loginEmail')
        self.wt.assert_url('http://localhost:5000/#/login')
        self.wt.set_value('#loginEmail', 'admin')
        self.wt.set_value('#loginPassword', 'secret')
        self.wt.send_key('#loginPassword', 'ENTER')

        self.wt.wait_for_visible('#ft-growl-notifications div.alert')

        # not using assert_text_in_elements because PyWebRunner has some problems with unicode
        # (at least with Chrome)
        self.assert_text_in_elements('#ft-growl-notifications div.alert', 'Invalid credentials')

    def test_admin_actions(self):
        self.wt.go('http://localhost:5000/')

        self.wt.wait_for_visible('#loginEmail')
        self.wt.assert_url('http://localhost:5000/#/login')
        self.wt.set_value('#loginEmail', 'admin')
        self.wt.set_value('#loginPassword', 'britecore')
        self.wt.send_key('#loginPassword', 'ENTER')

        self.wt.wait_for_visible('.card-block h4')
        self.wt.assert_url('http://localhost:5000/#/home')
        self.assert_text_in_elements('.card-block h4', 'Manage Clients')

        self.wt.click('.card[data-card="adminClient"] a')
        self.wt.wait_for_visible('#adminClientUi')
        self.wt.assert_url('http://localhost:5000/#/adminClient')

        self.wt.click('div#adminClientUi > button')
        self.wt.wait_for_visible('#frmclient')

        self.wt.set_value('#client_name', 'A rather new client')
        self.wt.set_value('#client_weight', 'abc')
        self.wt.click('#frmclient .modal-footer button.btn-primary')

        # should err
        self.wt.wait_for_visible('ul.ft-error-list > li')
        self.assert_text_in_elements('ul.ft-error-list > li', 'Client should have a valid numeric weight')

        self.wt.set_value('#client_weight', '2.42')
        self.wt.click('#frmclient .modal-footer button.btn-primary')
        self.wt.wait_for_invisible('#frmclient')

        # let the grid refresh. Maybe there's a better way
        self.wt.wait(1)
        self.assert_text_in_elements('#adminClientUi td', 'A rather new client')
        self.assert_text_in_elements('#adminClientUi td', '2.42')

        # logout
        self.wt.click('#lnkLogout')
        self.wt.wait_for_visible('#loginEmail')
        self.wt.assert_url('http://localhost:5000/#/login')

    def test_user_create_feature_and_admin_verify(self):
        self.wt.go('http://localhost:5000/')

        self.wt.wait_for_visible('#loginEmail')
        self.wt.assert_url('http://localhost:5000/#/login')
        self.wt.set_value('#loginEmail', 'sirius')
        self.wt.set_value('#loginPassword', 'sirius')
        self.wt.send_key('#loginPassword', 'ENTER')

        self.wt.wait_for_visible('.card-block h4')
        self.wt.assert_url('http://localhost:5000/#/home')
        self.assert_text_in_elements('.card-block h4', 'Propose Features')

        self.wt.click('.card[data-card="featuresClient"] a')
        self.wt.wait_for_visible('#ft-features-sortable')
        self.wt.assert_url('http://localhost:5000/#/featuresClient')

        # only reachable button
        self.wt.click('#ft-features-sortable > button')
        self.wt.wait_for_visible('#frmfeature')

        self.wt.set_value('#frmfeature fieldset > div:nth-child(1) input', 'A crazy feature')
        self.wt.set_value('#frmfeature fieldset > div:nth-child(2) textarea', 'Some value here')
        # area
        self.wt.set_value('#frmfeature fieldset > div:nth-child(6) select', '2')
        self.wt.click('#frmfeature .modal-footer button.btn-primary')
        self.wt.wait_for_invisible('#frmfeature')

        self.wt.wait(1)
        # the list will pick the change
        self.assert_text_in_elements('#ft-features-sortable', 'A crazy feature')

        # logout
        self.wt.click('#lnkLogout')
        self.wt.wait_for_visible('#loginEmail')
        self.wt.assert_url('http://localhost:5000/#/login')

        # see feature as admin
        self.wt.wait_for_visible('#loginEmail')
        self.wt.assert_url('http://localhost:5000/#/login')
        self.wt.set_value('#loginEmail', 'admin')
        self.wt.set_value('#loginPassword', 'britecore')
        self.wt.send_key('#loginPassword', 'ENTER')

        self.wt.click('.card[data-card="featuresStaff"] a')

        self.wt.wait(1)
        self.assert_text_in_elements('.ft-features-list', 'A crazy feature')

        # logout
        self.wt.click('#lnkLogout')
        self.wt.wait_for_visible('#loginEmail')
        self.wt.assert_url('http://localhost:5000/#/login')

if __name__ == '__main__':
    unittest.main()
