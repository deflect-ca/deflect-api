"""
A Django version of gen_site_config
"""

"""
I am literally less fond of no other code I have written.
"""

import os
import six
import logging

from django.conf import settings
from django.core.management.base import BaseCommand


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

        partition_config = settings.GSC_PARTITIONS
        partition_to_sites = self.partition_dnets(partition_config, all_data)
        for partition, sites in partition_to_sites.items():
            logging.error("number of sites in partition '%s': %s", partition, len(sites))
            self.write_config_if_changed(sites, os.path.join(output_location, partition), debug)

    def generate_site_file(self, blacklist_path, debug):
        return []

    def partition_dnets(self, partition_config, unsplit_dict):
        return {}

    def write_config_if_changed(self, new_config_dict, output_directory, debug):
        pass
