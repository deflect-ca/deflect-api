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
