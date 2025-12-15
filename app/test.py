import unittest
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app import create_app
from app import routes


class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_index_json(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)

    def test_index_xml(self):
        response = self.client.get('/?format=xml')
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('<response>', body)
        self.assertIn('<message>', body)

    def test_login_success_returns_token(self):
        password = 'secret123'
        user_record = {
            'id': 1,
            'email': 'user@example.com',
            'password_hash': generate_password_hash(password),
        }
        with patch.object(routes, 'fetch_one', return_value=user_record):
            response = self.client.post('/auth/login', json={'email': user_record['email'], 'password': password})

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('token', data)
        self.assertIn('expires_at', data)

    def test_login_invalid_credentials(self):
        with patch.object(routes, 'fetch_one', return_value=None):
            response = self.client.post('/auth/login', json={'email': 'missing@example.com', 'password': 'bad'})

        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)

    def test_add_shoe_requires_auth(self):
        response = self.client.post(
            '/shoes',
            json={'name': 'Test', 'brand_id': 1, 'size': 9, 'color': 'red', 'price': 100},
        )
        self.assertEqual(response.status_code, 401)

    def test_add_shoe_success(self):
        payload = {'name': 'Air', 'brand_id': 1, 'size': 10, 'color': 'blue', 'price': 120}

        with patch.object(routes.jwt, 'decode', return_value={'sub': 1, 'email': 'user@example.com'}):
            with patch.object(routes, 'execute', return_value=42):
                response = self.client.post(
                    '/shoes',
                    json=payload,
                    headers={'Authorization': 'Bearer faketoken'},
                )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data.get('id'), 42)
        self.assertEqual(data.get('message'), 'Shoe added')


if __name__ == '__main__':
    unittest.main()