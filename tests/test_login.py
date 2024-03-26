import unittest
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../api'))
from api.app import app


class LoginUserTestCase(unittest.TestCase):
    def setUp(self):
        """
        Set up the application for testing.
        """
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing purposes
        self.client = app.test_client()

    def test_login_success(self):
        """
        Test a successful login attempt.
        """
        # Example credentials; adjust based on your test user setup
        credentials = {
            "username": "testuser",
            "user_password": "correctpassword"
        }
        response = self.client.post('/user/login', data=credentials)
        # Assuming your login returns a redirect to a user-specific page on success
        self.assertEqual(response.status_code, 200)
        # Adjust the assertion based on the exact response your login logic provides

    def test_login_failure(self):
        """
        Test an unsuccessful login attempt due to incorrect credentials.
        """
        wrong_credentials = {
            "username": "testuser",
            "user_password": "wrongpassword"
        }
        response = self.client.post('/user/login', data=wrong_credentials)
        self.assertEqual(response.status_code, 401)
        # Ensure the response indicates a failure to log in, adjust as necessary
        response_data = json.loads(response.data)
        self.assertIn("Invalid username or password", response_data['message'])

    def tearDown(self):
        """
        Clean up after each test.
        """
        # Add any cleanup logic here, such as clearing the database or cache


if __name__ == '__main__':
    unittest.main()
