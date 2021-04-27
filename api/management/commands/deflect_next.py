from datetime import datetime

import os
import time
import logging
import yaml
import ssh_agent_setup

from django.core.management.base import BaseCommand
from api.models import Edge

from deflect_next.orchestration import old_to_new_site_dict
from deflect_next.orchestration import install_delta_config
from deflect_next.orchestration import generate_bind_config
from deflect_next.orchestration import decrypt_and_verify_cert_bundles
from deflect_next.orchestration import generate_nginx_config
from deflect_next.orchestration import generate_banjax_next_config

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
            '-y', '--sys',
            help='system sites.yml file'
        )
        parser.add_argument(
            '-m', '--mode',
            default='full',
            help='Default is not gen only mode'
        )
        parser.add_argument(
            '-k', '--key',
            help='SSH key file path'
        )

    def load_ssh_key(self, key_path):
        ssh_agent_setup.setup()
        ssh_agent_setup.addKey(os.path.expanduser(key_path))

    def measure_exec_time(self):
        self.start_time = time.time()

    def print_exec_time(self):
        logger.info("--- %s seconds ---" % (time.time() - self.start_time))

    def get_edge_list(self):
        edges = Edge.objects.all()
        edge_list = []

        for edge in edges:
            edge_list.append(edge.ip)

        return edge_list

    def handle(self, *args, **options):

        self.measure_exec_time()
        config = {}
        with open(options['config'], 'r') as file_config:
            config = yaml.load(file_config.read(), Loader=yaml.FullLoader)

        db_edge_list = self.get_edge_list()
        if len(db_edge_list) > 0:
            logger.info(f"config edge_ips:  \t{config['edge_ips']}")
            config['edge_ips'] = db_edge_list
            logger.info(f"replaced edge_ips:\t{config['edge_ips']}")

        logger.info(f"controller_domain:\t{config['controller_domain']}")
        logger.info(f"controller_ip:    \t{config['controller_ip']}")
        logger.info(f"edge_ips:         \t{config['edge_ips']}")
        logger.info(f"output_prefix:    \t{config['output_prefix']}")

        old_sites_yml = {}
        with open(options['sites'], "r") as file_sites:
            old_sites_yml = yaml.load(file_sites.read(), Loader=yaml.FullLoader)
            old_sites_timestamp = old_sites_yml["timestamp"]
            old_sites = old_sites_yml["remap"]

        timestamp = datetime.fromtimestamp(float(old_sites_yml["timestamp"]) / 1000.0)
        formatted_time = timestamp.strftime("%Y-%m-%d_%H:%M:%S")

        logger.info('old_to_new_site_dict')
        new_client_sites = old_to_new_site_dict.main(old_sites, old_sites_timestamp, config)

        system_sites = {}
        with open(options['sys'], "r") as f:
            system_sites = yaml.load(f.read(), Loader=yaml.FullLoader)

        all_sites = {'client': new_client_sites, 'system': system_sites}

        logger.info('generate_bind_config')
        generate_bind_config.main(config, all_sites, formatted_time)

        logger.info('decrypt_and_verify_cert_bundles')
        decrypt_and_verify_cert_bundles.main(all_sites, formatted_time, config)

        logger.info('generate_nginx_config')
        generate_nginx_config.main(all_sites, config, formatted_time)

        logger.info('generate_banjax_next_config')
        generate_banjax_next_config.main(config, all_sites, formatted_time)

        logger.info(f"load ssh key from: {options['key']}")
        self.load_ssh_key(options['key'])

        if options['mode'] == 'full':
            logger.info('install_delta_config')
            install_delta_config.main(config, all_sites, formatted_time, formatted_time)
        elif options['mode'] == 'edge':
            logger.info('edge update only')
            install_delta_config.edges(config, all_sites, formatted_time, formatted_time)
        else:
            logger.info('Mode should be set to: full, edge')

        self.print_exec_time()
