from django.test import TestCase
from api.models import Website
from marshmallow import ValidationError


class ModelTestCase(TestCase):
    # api/fixtures
    fixtures = ['data.yaml']

    def setUp(self):
        self.website_1 = Website.objects.get(pk=1)
        self.website_2 = Website.objects.get(pk=2)
        self.website_3 = Website.objects.get(pk=3)
        self.website_4 = Website.objects.get(pk=4)

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

        self.website_1.set_option('ns_unsubscribe_token', 'test')
        self.website_2.set_option('ns_unsubscribe_token', 'test')
        self.website_2.set_option('cachekey_param', 'test2')

        self.assertEqual(len(self.website_1.list_option()), 3)
        self.assertEqual(len(self.website_2.list_option()), 4)

        # test get_option fallback
        self.assertEqual(self.website_2.get_option('not_existed'), None)
        self.assertEqual(self.website_2.get_option('not_existed', 'fallback'), 'fallback')

        # assert exception on invalid option / key
        with self.assertRaises(ValidationError):
            self.website_1.set_option('not_existed', 'not_existed')

        # not correct type
        with self.assertRaises(ValidationError):
            self.website_1.set_option('approved', 87)  # suppose to be boolean

    def test_certificate(self):
        cert_1 = self.website_1.certificates.first()
        cert_4 = self.website_4.certificates.first()
        self.assertEqual(cert_1.hostnames, '*.example.com, example.com')
        self.assertEqual(cert_4.hostnames, 'example.edu')

    def test_record(self):
        record_1 = self.website_1.records.get(pk=1)
        self.assertEqual(record_1.type, 'A')
        self.assertEqual(record_1.hostname, 'ftp')
