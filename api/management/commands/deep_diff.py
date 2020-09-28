import yaml
import logging

from deepdiff import DeepDiff
from django.core.management.base import BaseCommand


class BadYaml(Exception):
    pass


class Command(BaseCommand):
    help = 'Execute deepdiff against two given yaml file'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '-f1', '--file1',
            help='YAML file to diff'
        )
        parser.add_argument(
            '-f2', '--file2',
            help='YAML file to diff'
        )
        parser.add_argument(
            '-o', '--output',
            default=None,
            help='Output YAML diff to file'
        )

    def handle(self, *args, **options):

        logging.info('Reading YAML %s ...', options['file1'])
        with open(options['file1'], "r") as yaml_file1:
            yaml_1_raw = yaml_file1.read()
            yaml_1 = yaml.load(yaml_1_raw, Loader=yaml.FullLoader)
            for i, l in enumerate(yaml_file1):
                pass

        logging.info('wc -l = %d', len(yaml_1_raw.split("\n")))

        logging.info('Reading YAML %s ...', options['file2'])
        with open(options['file2'], "r") as yaml_file2:
            yaml_2_raw = yaml_file2.read()
            yaml_2 = yaml.load(yaml_2_raw, Loader=yaml.FullLoader)
            for j, l in enumerate(yaml_file2):
                pass

        logging.info('wc -l = %d', len(yaml_2_raw.split("\n")))

        if "remap" not in yaml_1:
            raise BadYaml("yaml_1 doesen't have 'remap' key")
        if "remap" not in yaml_2:
            raise BadYaml("yaml_2 doesen't have 'remap' key")

        logging.info('Executing deepdiff against the given file ...')

        deepdiff = yaml.dump(dict(DeepDiff(
            yaml_1["remap"], yaml_2["remap"], ignore_order=True)))

        if options['output'] is None:
            logging.info(deepdiff)
            return

        logging.info('Writing output to %s', options['output'])
        with open(options['output'], "w") as output:
            output.write(deepdiff)
