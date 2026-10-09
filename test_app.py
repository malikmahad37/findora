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
        # Master data must exist in clean state
        self.assertGreaterEqual(Category.query.count(), 10)
        self.assertGreaterEqual(LocationCountry.query.count(), 1)
        self.assertGreaterEqual(LocationCity.query.count(), 5)
        # Admin user must exist
        self.assertGreaterEqual(User.query.filter_by(role='admin').count(), 1)

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
        # Create mock objects to verify the matching algorithm logic
        lost_wallet = Item(
            title='Black Leather Wallet',
            item_type='lost',
            category_id=1,
            color='Black',
            brand='J.',
            date_occurred=date.today()
        )
        found_wallet = Item(
            title="Black Men's Leather Wallet",
            item_type='found',
            category_id=1,
            color='Black',
            brand='J.',
            date_occurred=date.today()
        )

        match_res = calculate_match_score(lost_wallet, found_wallet)
        score = match_res['score']
        factors = match_res['factors']

        # Both have same category, similar name, same color
        self.assertGreaterEqual(score, 50)
        self.assertTrue(any('category' in f.lower() for f in factors))
        self.assertTrue(any('name' in f.lower() for f in factors))

    def test_auth_login_logout(self):
        # Test valid admin login
        resp = self.client.post('/auth/login', data={
            'email': 'admin@findora.pk',
            'password': 'Admin@1234'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Admin', resp.data)

        # Test logout
        resp_logout = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(resp_logout.status_code, 200)
        self.assertIn(b'Log In', resp_logout.data)

    def test_admin_access_control(self):
        # Non-logged in user accessing admin must be redirected
        resp = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)


if __name__ == '__main__':
    unittest.main()
