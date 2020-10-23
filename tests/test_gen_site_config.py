from io import StringIO
from django.conf import settings
from django.test import TestCase
from django.core.management import call_command

from api.models import YamlDiff
from api.management.commands.gen_site_config import Command as gsc


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

    def test_child_sites_get_parent_network(self):
        """
        Previously, every site would be assigned to the default network if it
        didn't have an override. We want child sites to have their parent's network.
        """
        datadict = {
            "example.com": {"network": "custom"},
            "test.example.com": {"network": "default"}
        }
        subsites = {"test.example.com": {"parent": "example.com"}}
        expected_datadict = {
            "example.com": {"network": "custom"},
            "test.example.com": {"network": "custom"}
        }
        self.assertEqual(gsc.child_sites_get_parent_network(
            datadict, subsites), expected_datadict)

    def test_remove_orphans_one_orphan(self):
        """
        The subsites dict is calculated without regard to blacklisted sites.
        Datadict will already have blacklisted sites removed, but may still have some dangling
        children that this function removes.
        In this test, the one site is an orphan and should be removed.
        """
        datadict = {"test.example.com": "blah"}
        subsites = {"test.example.com": {"parent": "example.com", "parent_creator_id": "blah2"}}
        self.assertEqual(gsc.remove_orphans(datadict, subsites, False), {})

    def test_remove_differently_owned_subsites_one_bad_subsite(self):
        """
        If a child site is owned by someone different than the parent site is,
        remove the child site.
        In this test, the subsite is should be removed.
        """
        datadict = {"example.com":
                    {"email": "joe@example.com"},
                    "test.example.com":
                        {"email": "joe@evil.com"}
                    }
        subsites = {"test.example.com":
                    {"parent": "example.com", "parent_creator_id": "blah3"}
                    }
        self.assertTrue("test.example.com" not in gsc.remove_differently_owned_subsites(datadict, subsites))

    def test_merge_subsite_records_under_parent(self):
        """
        In this test, the subsite has no dns_records. The subdomain should
        point to the root domain in a CNAME record.
        """
        datadict = {"example.com":
                    {"dns_records":
                    {"@": [
                        {"type": "A",
                        "value": ["x.x.x.x"]
                        }
                    ]}
                    },
                    "test.example.com":
                        {"dns_records": {}
                        }
                    }
        subsites = {"test.example.com":
                    {"parent": "example.com", "parent_creator_id": "blah3"}
                    }
        expected_merged = {"example.com":
                        {"dns_records":
                            {"@":
                            [{"type": "A",
                            "value": ["x.x.x.x"]
                            }
                            ],
                            "test":
                            [{"type": "CNAME",
                            "value": "example.com."
                            }
                            ]
                            }
                            },
                        "test.example.com": {}
                        }
        merged = gsc.merge_subsite_records_under_parent(datadict, subsites, False)
        self.assertTrue(merged == expected_merged)
