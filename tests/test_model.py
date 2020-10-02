import sys

from django.test import TestCase
from django.core.management import call_command
from api.models import Website


class ModelTestCase(TestCase):
    fixtures = ['data.yaml']

    def setUp(self):
        self.website_1 = Website.objects.get(pk=1)
        self.website_2 = Website.objects.get(pk=2)

    def test_website(self):
        self.assertEqual(self.website_1.url, 'example.com')
        self.assertEqual(self.website_2.url, 'example.net')

    def test_website_options(self):
        self.assertEqual(self.website_1.get_option('use_ssl'), False)
        self.assertEqual(self.website_2.get_option('use_ssl'), True)

        self.website_1.set_option('cache_time', 20)
        self.website_2.set_option('cache_time', 10)

        self.assertEqual(self.website_1.get_option('cache_time'), 20)
        self.assertEqual(self.website_2.get_option('cache_time'), 10)

        self.website_1.set_option('test_option', 'test')
        self.website_2.set_option('test_option', 'test')
        self.website_2.set_option('test_option2', 'test2')

        self.assertEqual(len(self.website_1.list_option()), 3)
        self.assertEqual(len(self.website_2.list_option()), 4)
