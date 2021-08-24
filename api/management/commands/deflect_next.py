from datetime import datetime
from pyaml_env import parse_config

import os
import time
import logging
import yaml
import ssh_agent_setup

from django.core.management.base import BaseCommand
from api.models import Edge
from deflect_next_orchestration.orchestration.install_delta_config import install_delta_config

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Execute deflect-next functions'
    origin_work_dir = None

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
            '-k', '--key',
            help='SSH key file path'
        )
        parser.add_argument(
            '-n', '--nextconf',
            help='Deflect next config file'
        )

    def change_workdir(self):
        if not self.origin_work_dir:
            self.origin_work_dir = os.getcwd()
            logger.info(f"Original workdir saved: {self.origin_work_dir}")
        project_root = os.path.abspath(os.path.dirname(__name__))
        target = f"{project_root}/deflect_next_orchestration/orchestration"
        os.chdir(target)
        logger.info(f"workdir changed to: {os.getcwd()}")

    def restore_workdir(self):
        os.chdir(self.origin_work_dir)
        logger.info(f"workdir restored to: {os.getcwd()}")

    def load_ssh_key(self, key_path):
        logger.info(f"load ssh key from: {key_path}")
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

        config = parse_config(options['config'])
        old_sites_yml = parse_config(options['sites'])
        system_sites = parse_config(options['sys'])
        orchestration_config = parse_config(options['nextconf'])

        # load ssh key for connecting to controller and edges
        self.load_ssh_key(options['key'])

        # Change python workdir to make deflect-next file path work
        self.change_workdir()

        install_delta_config(
            config=config,
            orchestration_config=orchestration_config,
            preload_old_client_sites=old_sites_yml,
            preload_system_sites=system_sites,
        )

        self.restore_workdir()
        self.print_exec_time()
