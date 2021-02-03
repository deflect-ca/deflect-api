from datetime import datetime

import logging
import yaml

from django.core.management.base import BaseCommand
from deflect_next.orchestration import old_to_new_site_dict

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Execute deflect-next functions'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '-c', '--config',
            help='config.yml file'
        )
        parser.add_argument(
            '-s', '--sites',
            help='sites.yml file'
        )
        parser.add_argument(
            '-o', '--output',
            help='output path for new sites.yml file'
        )


    def handle(self, *args, **options):

        old_sites_yml = {}
        with open(options['sites'], "r") as file_sites:
            old_sites_yml = yaml.load(file_sites.read(), Loader=yaml.FullLoader)

        time = datetime.fromtimestamp(float(old_sites_yml["timestamp"]) / 1000.0)
        formatted_time = time.strftime("%Y-%m-%d_%H:%M:%S")

        old_to_new_site_dict.main(old_sites_yml, options['output'])
