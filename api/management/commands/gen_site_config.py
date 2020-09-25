"""
A Django version of gen_site_config

I am literally less fond of no other code I have written.
"""

import glob
import ipaddress
import logging
import math
import ntpath
import os
import time
from operator import attrgetter

import six
import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from six import reraise as raise_

from api.models import Website  # pylint: disable=no-name-in-module


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
            default=False,
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

        partition_config = settings.GSC_PARTITIONS
        partition_to_sites = self.partition_dnets(partition_config, all_data)
        for partition, sites in partition_to_sites.items():
            logging.error("number of sites in partition '%s': %s", partition, len(sites))
            self.write_config_if_changed(sites, os.path.join(output_location, partition), debug)


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
        datadict = self.remove_orphans(datadict, dumb_subsites, debug)

        datadict = self.child_sites_get_parent_network(datadict, dumb_subsites)

        # XXX: There is no more email field, comment this line for now
        # datadict = self.remove_differently_owned_subsites(datadict, dumb_subsites)

        datadict = self.merge_subsite_records_under_parent(datadict, dumb_subsites, debug)

        return dict(datadict)

    def remove_differently_owned_subsites(self, datadict, dumb_subsites):
        for site_url in datadict.keys():
            parent_site_get = dumb_subsites.get(site_url)

            # Check if this is a subsite of another site `parent_site_get`
            if parent_site_get:
                # XXX these should exist because i'm assuming remove_orphans() goes first
                parent_site_url = parent_site_get.get("parent")
                parent_site_email = datadict[parent_site_url]["email"]
                if parent_site_email != datadict[site_url]["email"]:
                    logging.warning(
                        "WARNING!!!!\nThe logins for site %s and %s do not match - there's "
                        "a good chance someone is doing something malicious between %s and %s!\n"
                        "WARNING!!!", datadict[parent_site_url]["email"],
                        datadict[site_url]["email"], parent_site_url, site_url)
                    del datadict[site_url]
                    continue
        return datadict

    def merge_subsite_records_under_parent(self, datadict, dumb_subsites, debug):
        for site_url in datadict.keys():
            parent_site_get = dumb_subsites.get(site_url)

            # Check if this is a subsite of another site `parent_site_get`
            if parent_site_get:
                # XXX this should exist because i'm assuming remove_orphans() goes first
                parent_site_url = parent_site_get.get("parent")

                if debug:
                    logging.info("Site %s is a subsite of %s", site_url, parent_site_url)

                subsite_dns_records = datadict[site_url]["dns_records"]
                suffix = site_url.partition(parent_site_url)[0].strip(".")
                if debug:
                    logging.info("DNS suffix for %s is %s", site_url, suffix)

                # Subsite records override all parent records with the same label if records exist
                for record, values in six.iteritems(subsite_dns_records):
                    if not record or record == "@":
                        record = suffix
                    else:
                        record = record + "." + suffix
                    datadict[parent_site_url]["dns_records"][record] = values
                else:
                    # Even if subsite has no records, remove parent records for the subsite name
                    datadict[parent_site_url]["dns_records"][suffix] = []

                # This adds a CNAME record for every subsite base domain to the parent domain
                # e.g adds a blog.example.com CNAME record pointing to example.com.
                datadict[parent_site_url]["dns_records"].setdefault(suffix, [])
                datadict[parent_site_url]["dns_records"][suffix].append({
                    "type": "CNAME",
                    "value": parent_site_url + "."
                })

                # This block is concerned with cleaning any existing A
                # records to ensure that we deflect-protect existing
                # sites.
                clean_list = []
                for index, record in enumerate(datadict[parent_site_url]["dns_records"][suffix]):
                    if record["type"] == "A":
                        clean_list.append(index)

                for clean_elem in clean_list:
                    del datadict[parent_site_url]["dns_records"][suffix][clean_elem]

                # Delete the DNS records for the subsite but DON'T delete
                # the banjax etc config
                del datadict[site_url]["dns_records"]
        return datadict

    def child_sites_get_parent_network(self, datadict, dumb_subsites):
        for site_url in datadict.keys():
            maybe_parent_site = dumb_subsites.get(site_url)
            if maybe_parent_site:
                parent_url = maybe_parent_site["parent"]
                datadict[site_url]["network"] = datadict[parent_url]["network"]
        return datadict

    def remove_orphans(self, datadict, dumb_subsites, debug):
        for site_url in datadict.keys():
            parent_site_get = dumb_subsites.get(site_url)

            # Check if this is a subsite of another site `parent_site_get`
            if parent_site_get:
                parent_site_url = parent_site_get.get("parent")
                if parent_site_url not in datadict:
                    if debug:
                        logging.info("Found sub-site %s but not its parent %s. Is the parent "
                                    "blacklisted? Skipping sub-site!", site_url, parent_site_url)
                    del datadict[site_url]
                    continue
        return datadict

    def dict_for_site(self, site):
        """
        Creating yaml dict for a site
        """
        # Store dict of option for a site
        site_options = site.list_option()

        # Replacement of site.options.get()
        def safe_get_option(key, fallback=None):
            if key in site_options:
                return site_options[key]
            return fallback

        site_dict = {"url": site.url}

        default_cache_time = settings.GSC_DEFAULT_CACHE_TIME
        default_network = settings.GSC_DEFAULT_NETWORK

        # Parse all DNS records for this site
        site_dict["dns_records"] = self.parse_site_record_data(site)

        # Performed after all DNS record are parsed and added to `site_dict`
        # use_ssl should be True is SSL is enabled in the website control panel
        site_dict["https"] = safe_get_option("use_ssl") or False

        # Always use a TLS http_type if HTTPS is enabled
        http_type = safe_get_option("https_option", "http")
        # Override the current option only if set to "http" only:
        if site_dict["https"] and http_type == "http":
            http_type = "https"

        # Overide http_type to http when TLS is disabled.
        # This prevents an inconsistant state on autobrains where it is checking
        # for TLS based on the http_type option even when TLS is disabled in Dashboard.
        if not site_dict["https"]:
            http_type = "http"

        site_dict["http_type"] = http_type
        site_dict["letsencrypt"] = safe_get_option("cert_issuer") == "letsencrypt"
        site_dict["validate_tls"] = safe_get_option("enforce_valid_ssl") or False
        site_dict["origin_certificates"] = bool(site.certificates.all())
        # site_dict["email"] = site.creator.email

        # Include the filename for the user uploaded TLS certificate files.
        if safe_get_option("use_custom_ssl") and safe_get_option("ssl_bundle_time"):
            site_dict["tls_bundle"] = safe_get_option("ssl_bundle_time")

        # We default to saving visitor logs if option True, or option is not set
        site_dict["disable_logging"] = (not safe_get_option("save_visitor_logs", True))
        site_dict["origin"] = site.ip_address
        site_dict["cache_time"] = int(safe_get_option("cache_time", default_cache_time))

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
            maybe_value = safe_get_option(option, False)
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

        site_dict["network"] = safe_get_option("network", default_network)

        # XXX: Is hidden_domain used by Deflect?
        site_dict["hidden"] = site.hidden_domain.lower()
        site_dict["awstats_password"] = site.awstats_password
        site_dict["banjax_password"] = (site.banjax_auth_hash or '').strip()

        # XXX: Maybe simplify so this is always a list
        banjax_path = (site.admin_key or "")
        if len(safe_get_option("banjax_path", [])) > 0:
            if banjax_path:
                banjax_path = list(set(site_options["banjax_path"] + [banjax_path]))
            else:
                banjax_path = site_options["banjax_path"]

        site_dict["banjax_path"] = banjax_path

        site_dict["banjax_sha_inv"] = safe_get_option("banjax_sha_inv", False)
        site_dict["banjax_captcha"] = safe_get_option("banjax_captcha", False)
        site_dict["user_banjax_sha_inv"] = safe_get_option("user_banjax_sha_inv", False)

        site_dict["ns_on_deflect"] = safe_get_option("ns_on_deflect", False)
        site_dict["ns_monitoring_disabled"] = safe_get_option("ns_monitoring_disabled", False)

        if site.ats_purge_secret:
            site_dict["ats_purge_secret"] = site.ats_purge_secret
        else:
            logging.warning("XXX site %s has no ats_purge_secret", site.url)
            site_dict["ats_purge_secret"] = settings.GSC_REMAP_PURGE_DEFAULT_SECRET

        return site_dict

    def parse_site_record_data(self, site):
        """
        Read all DNS records for site and perform record validation
        """
        dns_records = {}
        records = site.records.all()
        for record in sorted(records, key=attrgetter("type")):
            for hostname, data in six.iteritems(self.record_to_dicts(record, site)):
                dns_records.setdefault(hostname, [])
                dns_records[hostname].append(data)
        return dns_records

    def record_to_dicts(self, record, site):
        """
        Note the plural "dicts" because the MX -> A record thing returns two dicts.
        """
        dicts = {}
        hostname = record.hostname.strip().strip(".")
        site_url = site.url

        if not hostname:
            hostname = "@"

        value = record.value.strip()
        record_type = record.type

        # We need to remap @ MX records that point to the root
        # domain. We do this by creating MX records for something
        # called "deflectmx" which is then set to be their MX.
        if record_type == "MX" and value == "%s." % site_url:
            dicts["deflectmx"] = {
                "type": "A",
                "value": site.ip_address
            }
            value = "deflectmx.%s." % site_url

        if (record_type == "CNAME" and hostname == "mail" and
                value in ["@", site_url, site_url + "."]):
            record_type = "A"
            value = site.ip_address

        # TXT records generally need leading and trailing quotes
        # They also need to be split if they are too long (see RFC4408, section 3.1.3)
        if record_type == "TXT":
            value = '"{}"'.format(value)

        # Properly set up MX records - use the priority
        if record_type == "MX":
                # We now just use a priority column and not a TTL column
            value = [int(record.priority), value]

        # We need all the necessary parameters for a SRV records to be set, otherwise we ignore
        if record_type == "SRV":
            if all([hasattr(record, field) for field in ["priority", "weight", "port"]]):
                value = [int(record.priority), int(record.weight), int(record.port), value]
            else:
                logging.info("Skipping SRV record %s for website %s due to missing "
                            "parameters", hostname, site.url)
                return {}

        # Remove www. CNAME records, and A and NS records for the root. This is performed
        # by autobrains when generating the zonefile. We should do it here to ensure
        # new DNS code is producing the same clients.yml output
        is_root = hostname in ["@", site_url, site_url + "."]
        if (is_root and record_type in ["A", "NS"]) or hostname == "www":
            logging.debug("Skipping %s record %s with value %s", record_type, hostname, value)
            return {}

        # XXX these invalid A records should not get this far, but they do. I've spent
        # so much time trying to find where they come from -- CNAME records getting their
        # type changed to A records (but staying pointing to a hostname) -- to no avail.
        if record_type == "A":
            try:
                ipaddress.ip_address(value)  # this raises ValueError if it can't parse an IP
            except ValueError:
                logging.debug("Skipping %s record %s with value %s", record_type, hostname, value)
                return {}

        dicts[hostname] = {"type": record_type, "value": value}
        return dicts

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
        dnet_to_partition = self.invert_partition_config(partition_config)
        partition_to_sites = {}
        for site_url, site_config in six.iteritems(unsplit_dict):
            if site_config["network"] not in dnet_to_partition:
                raise ValueError("dnet %s not assigned to a partition" % site_config["network"])
            partition = dnet_to_partition[site_config["network"]]
            if partition not in partition_to_sites:
                partition_to_sites[partition] = {}
            partition_to_sites[partition][site_url] = site_config
        return partition_to_sites

    def invert_partition_config(self, partition_to_config):
        dnet_to_partition = {}
        for partition, partition_config in six.iteritems(partition_to_config):
            for dnet in partition_config["dnets"]:
                if dnet in dnet_to_partition:
                    raise ValueError("dnet can only belong to one partition")
                dnet_to_partition[dnet] = partition
        return dnet_to_partition

    def write_config_if_changed(self, new_config_dict, output_directory, debug):
        if not os.path.isdir(output_directory):
            if 'TESTING' in os.environ:
                os.mkdir(output_directory)
            else:
                raise RuntimeError(
                    "Output directory %s not found, please mkdir it" % output_directory)

        new_timestamp_ms = int(math.floor(time.time() * 1000))  # goes in the file
        new_timestamp_s = int(new_timestamp_ms / 1000)  # goes in the filename

        new_filename = settings.GSC_OUTPUT_FILE.format(new_timestamp_s)
        new_filepath = os.path.abspath(os.path.join(output_directory, new_filename))

        maybe_old_filepath = self.get_most_recent_config(output_directory)
        # if maybe_old_filepath:
        #    old_timestamp_s = self.filepath_to_timestamp(maybe_old_filepath)
        #else:
        #    old_timestamp_s = new_timestamp_s - 1  # white lie? XXX


        new_config_dict = {"remap": new_config_dict, "timestamp": new_timestamp_ms}
        new_config_dict = yaml.load(
            yaml.safe_dump(
                new_config_dict), Loader=yaml.FullLoader)  # unicode vs str diffs otherwise
        # old_config_dict = None
        if maybe_old_filepath:
            with open(maybe_old_filepath) as rfile:
                old_config_dict = yaml.load(rfile, Loader=yaml.FullLoader)
        else:
            pass
            # old_config_dict = new_config_dict  # white lie? XXX

        # TODO: Stat/YamlDiff
        # compute it now for the diff to see if we should proceed, but save() later
        # yaml_diff = YamlDiff(old_timestamp_s, new_timestamp_s,
        #                    old_config_dict, new_config_dict,
        #                    output_directory)
        if not maybe_old_filepath:
            logging.info("First run in this output directory.")
        # elif yaml_diff.diff == {}:
        #     logging.info("No site changes detected.")
        #     return
        else:
            logging.info("Site changes detected.")

        logging.info("Deflect dashboard configuration updated")

        if debug:
            return

        new_config_yaml = yaml.safe_dump(new_config_dict, default_flow_style=False)
        with open(new_filepath, "w") as wfile:
            wfile.write(new_config_yaml)

        if os.path.exists(os.path.join(output_directory, "site.yml")):
            os.remove(os.path.join(output_directory, "site.yml"))

        os.symlink(new_filepath, os.path.join(output_directory, "site.yml"))

        logging.info("Generated updated site.yml at %s", new_filepath)

        # TODO: Stat/YamlDiff
        # try:
        #     Stat(new_timestamp_s, new_config_dict, output_directory).save()
        #     logger.info("Saved Stat for %s" % new_timestamp_s)
        #     yaml_diff.save()
        #     logger.info("Saved YamlDiff for %s" % new_timestamp_s)
        # except Exception:
        #     logger.error("Something wrong with Stat or YamlDiff")
        #     logger.error("%s" % traceback.format_exc())

    def get_most_recent_config(self, output_location):
        configs = sorted(glob.glob(output_location + "/*.site.yml"))
        if configs:
            return configs[-1]
        else:
            return None

    def filepath_to_timestamp(self, filepath):
        maybe_timestamp = ntpath.basename(filepath).split(".")[0]
        try:
            int(maybe_timestamp)
        except ValueError:
            raise_(RuntimeError("filename has no timestamp? '%s'" % filepath), None)
        return maybe_timestamp
