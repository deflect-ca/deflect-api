import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Execute deflect-next functions'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '-i', '--input',
            help='input json file'
        )
        parser.add_argument(
            '-o', '--output',
            help='output json file'
        )


    def handle(self, *args, **options):
        with open(options['input'], 'r') as json_file:
            openapi = json.load(json_file)

            openapi['info']['version'] = 'v0.1'  # XXX hard code version

            should_be_removed = []
            for api_path in openapi['paths']:
                if api_path.endswith('{format}'):
                    print(api_path)
                    should_be_removed.append(api_path)

            for api_path in should_be_removed:
                openapi['paths'].pop(api_path)

            with open(options['output'], 'w') as output:
                print(f"Writing output to {options['output']}")
                json.dump(openapi, output, indent=2)
