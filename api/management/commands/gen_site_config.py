"""
A Django version of gen_site_config

I am literally less fond of no other code I have written.
"""

import os
import logging
import six

from django.conf import settings
from django.core.management.base import BaseCommand
from api.models import Website


class Command(BaseCommand):
    help = 'Generating site.yml according to database'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '-o', '--output',
            default=settings.GSC_OUTPUT_LOCATION,
            help='Directory to store generate YAML files'
        )
        parser.add_argument(
            '-b', '--blacklist',
            default=settings.GSC_BLACKLIST_FILE,
            help='Name of blacklist file in the output directory'
        )
        parser.add_argument(
            '-d', '--debug',
            default=settings.DEBUG,
            action='store_true',
            help='Debug mode'
        )

    def handle(self, *args, **options):
        """
        This can either be called from the command line via manage.py
        or by a scheduled task.
        """
        logging.info('Running gen_site_config command')
        blacklist_file = options['blacklist']
        output_location = options['output']
        debug = options['debug']

        if not os.path.isabs(blacklist_file):
            blacklist_path = os.path.join(output_location, blacklist_file)
        else:
            blacklist_path = blacklist_file

        all_data = self.generate_site_file(blacklist_path, debug)
        logging.debug(all_data)

        """
        partition_config = settings.GSC_PARTITIONS
        partition_to_sites = self.partition_dnets(partition_config, all_data)
        for partition, sites in partition_to_sites.items():
            logging.error("number of sites in partition '%s': %s", partition, len(sites))
            self.write_config_if_changed(sites, os.path.join(output_location, partition), debug)
        """

    def generate_site_file(self, blacklist_path, debug):
        """
        Iterate over each website and extract its config information and DNS records
        """
        if os.path.isfile(blacklist_path):
            with open(blacklist_path) as blacklist_f:
                blacklist_list = [i.strip() for i in blacklist_f.readlines()]
        else:
            blacklist_list = []

        # Only load the set of active sites which should be included in clients.yml
        site_details = [site for site in Website.objects.all()
                        if self.should_include_site(site, blacklist_list)]

        dumb_subsites = self.find_subsites(site_details)

        datadict = {site.url: self.dict_for_site(site) for site in site_details}

        # remove_orphans() should go first or the next ones will fail
        # trying to find missing parents
        #datadict = remove_orphans(datadict, dumb_subsites, debug)

        #datadict = child_sites_get_parent_network(datadict, dumb_subsites)

        #datadict = remove_differently_owned_subsites(datadict, dumb_subsites)

        #datadict = merge_subsite_records_under_parent(datadict, dumb_subsites, debug)

        return dict(datadict)

    def dict_for_site(self, site):
        """
        Creating yaml dict for a site
        """
        # TODO: Limit the use of site.get_option, use site_options dict
        # Store dict of option for a site
        site_options = site.list_option()

        site_dict = {"url": site.url}

        default_cache_time = settings.GSC_DEFAULT_CACHE_TIME
        default_network = settings.GSC_DEFAULT_NETWORK

        # Parse all DNS records for this site
        # TODO: site_dict["dns_records"] = parse_site_record_data(site)

        # Performed after all DNS record are parsed and added to `site_dict`
        # use_ssl should be True is SSL is enabled in the website control panel
        site_dict["https"] = site.get_option("use_ssl") or False

        # Always use a TLS http_type if HTTPS is enabled
        http_type = site.get_option("https_option", "http")
        # Override the current option only if set to "http" only:
        if site_dict["https"] and http_type == "http":
            http_type = "https"

        # Overide http_type to http when TLS is disabled.
        # This prevents an inconsistant state on autobrains where it is checking
        # for TLS based on the http_type option even when TLS is disabled in Dashboard.
        if not site_dict["https"]:
            http_type = "http"

        site_dict["http_type"] = http_type
        site_dict["letsencrypt"] = site.get_option("cert_issuer") == "letsencrypt"
        site_dict["validate_tls"] = site.get_option("enforce_valid_ssl") or False
        # TODO: site_dict["origin_certificates"] = bool(site.certificates)
        # TODO: site_dict["email"] = site.creator.email

        # Include the filename for the user uploaded TLS certificate files.
        if site.get_option("use_custom_ssl") and site.get_option("ssl_bundle_time"):
            site_dict["tls_bundle"] = site.get_option("ssl_bundle_time")

        # We default to saving visitor logs if option True, or option is not set
        site_dict["disable_logging"] = (not site.get_option("save_visitor_logs", True))
        site_dict["origin"] = site.ip_address
        site_dict["cache_time"] = int(site.get_option("cache_time", default_cache_time))

        # These are all ints and bools
        for option in ["allow_http_delete_push",
                    "banjax_whitelist_include_auth",
                    "cachecontrol",
                    "cache_cookies",
                    "confremap",
                    "no_www",
                    "origin_http_port",
                    "origin_https_port",
                    "www_only"]:
            if option in site_options:
                site_dict[option] = site_options[option]

        # These are both strings. Previously, they were optionally set in
        # override.yml. There's been at least one bug around passing an
        # empty value when actually we want to omit the option if it's blank,
        # so I'm checking that here.
        for option in ["cachekey_param",
                    "origin_object"]:
            maybe_value = site.get_option(option, False)
            if maybe_value and maybe_value != "":  # being extra explicit
                site_dict[option] = site_options[option]

        # These are list types. Same paranoia as with the string types above
        # regarding empty values.
        for option in ["additional_domain_prefix",
                    "add_banjax_whitelist",
                    "banjax_path_exceptions",
                    "cache_exceptions"]:
            if option in site_options:
                vals = site_options[option]
                vals = [v for v in vals if v is not None]
                vals = [v for v in vals if v != ""]
                if len(vals) > 0:
                    site_dict[option] = vals

        # XXX dashboard uses plural because it is a list,
        # autodeflect uses singular because of historical reasons.
        if "banjax_regex_banners" in site_options:
            brbs = site_options["banjax_regex_banners"]
            brbs = [brb for brb in brbs if self.valid_brb(brb)]
            if len(brbs) > 0:
                site_dict["banjax_regex_banner"] = brbs

        site_dict["network"] = site.get_option("network", default_network)

        # XXX: Is hidden_domain used by Deflect?
        site_dict["hidden"] = site.hidden_domain.lower()
        site_dict["awstats_password"] = site.awstats_password
        site_dict["banjax_password"] = (site.banjax_auth_hash or '').strip()

        # XXX: Maybe simplify so this is always a list
        banjax_path = (site.admin_key or "")
        if len(site.get_option("banjax_path", [])) > 0:
            if banjax_path:
                banjax_path = list(set(site_options["banjax_path"] + [banjax_path]))
            else:
                banjax_path = site_options["banjax_path"]

        site_dict["banjax_path"] = banjax_path

        site_dict["banjax_sha_inv"] = site.get_option("banjax_sha_inv", False)
        site_dict["banjax_captcha"] = site.get_option("banjax_captcha", False)
        site_dict["user_banjax_sha_inv"] = site.get_option("user_banjax_sha_inv", False)

        site_dict["ns_on_deflect"] = site.get_option("ns_on_deflect", False)
        site_dict["ns_monitoring_disabled"] = site.get_option("ns_monitoring_disabled", False)

        if site.ats_purge_secret:
            site_dict["ats_purge_secret"] = site.ats_purge_secret
        else:
            logging.warning("XXX site %s has no ats_purge_secret", site.url)
            site_dict["ats_purge_secret"] = settings.GSC_REMAP_PURGE_DEFAULT_SECRET

        return site_dict

    def valid_brb(self, brb):
        """
        a banjax_regex_banner looks like:
        {
            "hits_per_interval": 0,
            "interval": 1,
            "regex": {
                "method": "GET",
                "ua": ".*python-requests.*",
                "url": ".*"
            }
        }
        """
        if not isinstance(brb.get("hits_per_interval"), six.integer_types):
            return False
        if not isinstance(brb.get("interval"), six.integer_types):
            return False
        if not isinstance(brb.get("regex"), dict):
            return False
        regex = brb["regex"]
        if not isinstance(regex.get("method"), (str, six.text_type)):
            return False
        if not isinstance(regex.get("ua"), (str, six.text_type)):
            return False
        if not isinstance(regex.get("url"), (str, six.text_type)):
            return False
        return True

    def should_include_site(self, site, blacklist_list):
        """
        Decide if a site should be included in the clients.yml
        """
        if site.url in blacklist_list:
            return False

        if site.status < 3 and site.status != -1:
            return False

        return True

    def find_subsites(self, site_details):
        dumb_subsites = {}
        for site in site_details:
            for checksite in site_details:
                if site.url != checksite.url and checksite.url.endswith('.' + site.url):
                    # checksite is a subsite of site
                    dumb_subsites[checksite.url] = {
                        "parent": site.url,
                        "parent_creator_id": site.creator_id
                    }
        return dumb_subsites

    def partition_dnets(self, partition_config, unsplit_dict):
        return {}

    def write_config_if_changed(self, new_config_dict, output_directory, debug):
        pass
