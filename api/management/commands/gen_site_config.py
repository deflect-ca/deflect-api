"""
A Django version of gen_site_config

I am literally less fond of no other code I have written.
"""

import os
import logging

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
        return site

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
