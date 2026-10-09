import unittest
from app import create_app, db
from app.models import User, Item, Category, LocationCountry, LocationCity, Claim, Message
from app.services.matching import calculate_match_score, find_matches
from datetime import date, timedelta


class CampusFindTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_database_populated(self):
        self.assertGreaterEqual(User.query.count(), 3)
        self.assertGreaterEqual(Item.query.count(), 4)
        self.assertGreaterEqual(Category.query.count(), 10)
        self.assertGreaterEqual(LocationCountry.query.count(), 1)
        self.assertGreaterEqual(LocationCity.query.count(), 5)

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'FINDORA', response.data)
        self.assertIn(b'Lost Something? Find It', response.data)

    def test_browse_page(self):
        response = self.client.get('/browse')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Browse Lost & Found Items', response.data)

    def test_api_stats(self):
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('total_lost', data)
        self.assertIn('total_found', data)
        self.assertIn('total_users', data)

    def test_api_location_cascade(self):
        pk = LocationCountry.query.filter_by(name='Pakistan').first()
        self.assertIsNotNone(pk)
        response = self.client.get(f'/api/regions/{pk.id}')
        self.assertEqual(response.status_code, 200)
        regions = response.get_json()
        self.assertGreater(len(regions), 0)

    def test_smart_matching_algorithm(self):
        # Retrieve test wallet items
        lost_wallet = Item.query.filter_by(item_type='lost', title='Black Leather Wallet').first()
        found_wallet = Item.query.filter_by(item_type='found', title="Black Men's Leather Wallet").first()
        self.assertIsNotNone(lost_wallet)
        self.assertIsNotNone(found_wallet)

        match_res = calculate_match_score(lost_wallet, found_wallet)
        score = match_res['score']
        factors = match_res['factors']

        # Both have same category, similar name, same city, same color
        self.assertGreaterEqual(score, 60)
        self.assertTrue(any('category' in f.lower() for f in factors))
        self.assertTrue(any('name' in f.lower() for f in factors))

    def test_auth_login_logout(self):
        # Test valid login
        resp = self.client.post('/auth/login', data={
            'email': 'demo@findora.pk',
            'password': 'Demo@1234'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Ahmad Raza', resp.data)

        # Test logout
        resp_logout = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(resp_logout.status_code, 200)
        self.assertIn(b'Log In', resp_logout.data)

    def test_admin_access_control(self):
        # Non-logged in user accessing admin must be redirected
        resp = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

        # Regular user accessing admin must be 403 forbidden
        self.client.post('/auth/login', data={
            'email': 'demo@findora.pk',
            'password': 'Demo@1234'
        })
        resp_user_admin = self.client.get('/admin/')
        self.assertEqual(resp_user_admin.status_code, 403)


if __name__ == '__main__':
    unittest.main()
