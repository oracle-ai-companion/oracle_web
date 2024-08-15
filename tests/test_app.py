import unittest
from app import app

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True 

    def test_home_status_code(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_data(self):
        response = self.app.get('/')
        self.assertIn(b'Welcome to the Discord Bot Dashboard', response.data)

    def test_login_redirect(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_dashboard_redirect_when_not_logged_in(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to login

if __name__ == '__main__':
    unittest.main()
