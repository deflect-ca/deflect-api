from io import StringIO
from django.conf import settings
from django.test import TestCase
from django.core.management import call_command
from api.models import YamlDiff


class GenSiteConfigTestCase(TestCase):
    fixtures = ['data.yaml']

    def test_01_gen_site_config(self):
        out = StringIO()
        call_command('gen_site_config',  # GSC_OUTPUT_LOCATION=/tmp in .env.ci
            stdout=out, test=True)  # Enable --test to always write YAML
        self.assertIn('gen_site_config succeed', out.getvalue())

        # Test if YamlDiff was recorded
        ydiff = YamlDiff.objects.first()
        self.assertNotEqual(ydiff, None)

    def test_02_deep_diff(self):
        out, err = StringIO(), StringIO()
        call_command('deep_diff',
            stdout=out, stderr=err,
            file1='tests/sample/site.yml',
            file2='{}/part1/site.yml'.format(  # GSC_DEFAULT_NETWORK / GSC_PARTITIONS
                settings.GSC_OUTPUT_LOCATION))
        self.assertIn('file1 and file2 are identical', out.getvalue())
