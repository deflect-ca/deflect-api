import sys

from django.test import TestCase
from django.core.management import call_command
from api.models import Website


class ModelTestCase(TestCase):
    fixtures = ['data.yaml']

    def setUp(self):
        self.website_1 = Website.objects.get(pk=1)
        self.website_2 = Website.objects.get(pk=2)

    def test_model_imported(self):
        self.assertEqual(self.website_1.url, 'example.com')
        self.assertEqual(self.website_2.url, 'example.net')
