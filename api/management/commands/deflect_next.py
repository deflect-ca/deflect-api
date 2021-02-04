from datetime import datetime

import os
import logging
import yaml

from django.core.management.base import BaseCommand
from deflect_next.orchestration import old_to_new_site_dict
from deflect_next.orchestration import install_delta_config
from deflect_next.orchestration import generate_bind_config
from deflect_next.orchestration import generate_nginx_config
from deflect_next.orchestration import generate_auth_server_config

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
            help='output path for new sites.yml file (only dir)'
        )
        parser.add_argument(
            '-p', '--prod',
            default=False,
            action='store_true',
            help='Default is staging mode'
        )


    def handle(self, *args, **options):

        old_sites_yml = {}
        with open(options['sites'], "r") as file_sites:
            old_sites_yml = yaml.load(file_sites.read(), Loader=yaml.FullLoader)

        time = datetime.fromtimestamp(float(old_sites_yml["timestamp"]) / 1000.0)
        formatted_time = time.strftime("%Y-%m-%d_%H:%M:%S")
        output_dir = f"{options['output']}/{formatted_time}"

        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        logger.info('old_to_new_site_dict')
        old_to_new_site_dict.main(old_sites_yml, options['output'])

        config = {}
        with open(options['config'], 'r') as file_config:
            config = yaml.load(file_config.read(), Loader=yaml.FullLoader)

        all_sites = {}
        with open(f"{output_dir}/new-sites.yml", 'r') as file_all_sites:
            all_sites = yaml.load(file_all_sites.read(), Loader=yaml.FullLoader)

        if not options['prod']:
            all_sites = install_delta_config.add_staging_zone(all_sites, config)

        print(all_sites)

        logger.info('generate_bind_config')
        generate_bind_config.main(config, all_sites, formatted_time, output_prefix=output_dir)

        # logger.info('decrypt_and_verify_cert_bundles')
        # decrypt_and_verify_cert_bundles.main(all_sites, formatted_time)

        logger.info('generate_nginx_config')
        generate_nginx_config.main(all_sites, config, formatted_time, output_prefix=output_dir)

        logger.info('generate_auth_server_config')
        generate_auth_server_config.main(config, all_sites, formatted_time, output_prefix=output_dir)

        install_delta_config.main(config, all_sites, formatted_time, formatted_time, output_prefix=output_dir)