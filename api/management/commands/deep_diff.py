import logging
import yaml

from deepdiff import DeepDiff
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


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

        logger.info('Reading YAML %s ...', options['file1'])
        with open(options['file1'], "r") as yaml_file1:
            yaml_1_raw = yaml_file1.read()
            yaml_1 = yaml.load(yaml_1_raw, Loader=yaml.FullLoader)

        logger.info('wc -l = %d', len(yaml_1_raw.split("\n")))

        logger.info('Reading YAML %s ...', options['file2'])
        with open(options['file2'], "r") as yaml_file2:
            yaml_2_raw = yaml_file2.read()
            yaml_2 = yaml.load(yaml_2_raw, Loader=yaml.FullLoader)

        logger.info('wc -l = %d', len(yaml_2_raw.split("\n")))

        if "remap" not in yaml_1:
            raise BadYaml("yaml_1 doesen't have 'remap' key")
        if "remap" not in yaml_2:
            raise BadYaml("yaml_2 doesen't have 'remap' key")

        logger.info('Executing deepdiff against the given file ...')

        deepdiff = dict(DeepDiff(
            yaml_1["remap"], yaml_2["remap"], ignore_order=True))
        deepdiff_yaml = yaml.dump(deepdiff)

        if options['output'] is None:
            logger.info(deepdiff_yaml)
        else:
            logger.info('Writing output to %s', options['output'])
            with open(options['output'], "w") as output:
                output.write(deepdiff_yaml)

        if deepdiff == {}:
            self.stdout.write(self.style.SUCCESS('file1 and file2 are identical'))
        else:
            self.stderr.write(self.style.ERROR('file and file2 are different'))
