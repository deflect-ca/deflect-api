from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class RestFrameworkTestCase(TestCase):
    fixtures = ["data.yaml"]

    def setUp(self):
        # Create test user
        self.user = User.objects.create_superuser(
            "testuser", "testuser@example.com", "testpassword")
        self.token = Token.objects.create(user=self.user).key
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

    def test_01_website_list(self):
        response = self.client.get("/api/website/list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)

    def test_02_website_create_without_options(self):
        # without nested options
        response = self.client.post("/api/website/create", {
            "url": "test.com",
            "status": 0,
            "ip_address": "127.0.0.1",
            "admin_key": "/wp-admin"
        })

        obj = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(obj["url"], "test.com")
        self.assertEqual(obj["options"], [])

    def test_03_website_create_with_options(self):
        # with nested options
        options = [
            {
                "name": "use_ssl",
                "data": True
            },
            {
                "name": "use_custom_ssl",
                "data": False
            }
        ]
        response = self.client.post("/api/website/create", {
            "url": "test2.com",
            "status": 0,
            "ip_address": "127.0.0.1",
            "admin_key": "/wp-admin",
            "options": options
        }, format='json')

        obj = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(obj["url"], "test2.com")
        self.assertEqual(obj["options"], options)

    def test_04_website_create_with_option_error(self):
        # option_not_existed
        options = [
            {
                "name": "option_not_existed",
                "data": True
            }
        ]
        response = self.client.post("/api/website/create", {
            "url": "test3.com",
            "status": 0,
            "ip_address": "127.0.0.1",
            "admin_key": "/wp-admin",
            "options": options
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown field", response.json()[0])

        # invalid data type for option
        options = [
            {
                "name": "cache_time",  # should be integer
                "data": "not integer"
            }
        ]
        response = self.client.post("/api/website/create", {
            "url": "test3.com",  # also make sure if DB rollback is working
            "status": 0,
            "ip_address": "127.0.0.1",
            "admin_key": "/wp-admin",
            "options": options
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn("Not a valid integer", response.json()[0])

        # invalid field name
        options = [
            {
                "name": "cache_time",  # should be integer
                "value": 20
            }
        ]
        response = self.client.post("/api/website/create", {
            "url": "test3.com",
            "status": 0,
            "ip_address": "127.0.0.1",
            "admin_key": "/wp-admin",
            "options": options
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn("KeyError", response.json()[0])

    def test_05_website_detail(self):
        response = self.client.get("/api/website/1")
        self.assertEqual(response.status_code, 200)

        obj = response.json()
        self.assertEqual(obj['url'], 'example.com')
        self.assertEqual(obj['ip_address'], '192.0.2.0')  # later test modify in 06

        options = [
            {
                "name": "use_ssl",
                "data": False
            },
            {
                "name": "cache_time",
                "data": 10
            }
        ]
        self.assertEqual(obj['options'], options)

    def test_06_website_modify_without_options(self):
        # test partial update
        response = self.client.put("/api/website/1/modify", {
            "ip_address": "127.0.0.1"
        }, format='json')

        obj = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(obj['ip_address'], "127.0.0.1")

    def test_07_website_modify_with_options(self):
        # Add 1 option, without modify anything
        response = self.client.put("/api/website/1/modify", {
            "options": [
                {
                    "name": "use_custom_ssl",
                    "data": False
                }
            ]
        }, format='json')

        obj = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(obj['options'], [
            {
                "name": "use_ssl",
                "data": False
            },
            {
                "name": "cache_time",
                "data": 10
            },
            {
                "name": "use_custom_ssl",
                "data": False
            }
        ])

        # Modify 2 options
        response = self.client.put("/api/website/1/modify", {
            "options": [
                {
                    "name": "use_ssl",
                    "data": True
                },
                {
                    "name": "cache_time",
                    "data": 87
                },
                # no use_custom_ssl, should left unchanged
            ]
        }, format='json')

        obj = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(obj['options'], [
            {
                "name": "use_ssl",
                "data": True
            },
            {
                "name": "cache_time",
                "data": 87
            },
            {
                "name": "use_custom_ssl",
                "data": False
            }
        ])

    def test_08_website_modify_with_options_and_err(self):
        # option_not_existed
        response = self.client.put("/api/website/1/modify", {
            "options": [
                {
                    "name": "option_not_existed",
                    "data": False
                }
            ]
        }, format='json')

        obj = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown field", response.json()[0])

        # field invalid
        response = self.client.put("/api/website/1/modify", {
            "options": [
                {
                    "name": "cache_time",
                    "value": False
                }
            ]
        }, format='json')

        obj = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("KeyError", response.json()[0])
