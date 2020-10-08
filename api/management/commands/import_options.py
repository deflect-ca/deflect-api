import json
import logging

from django.core.management.base import BaseCommand
from api.models import WebsiteOption


class Command(BaseCommand):
    help = 'Import website options json'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '-f', '--file',
            help='JSON file to import'
        )

    def handle(self, *args, **options):
        json_arr = None
        with open(options['file'], "r") as json_file:
            json_arr = json.loads(json_file.read())

        logging.info('Load json with length = %s', str(len(json_arr)))

        if len(json_arr) > 0:
            bulk_arr = []
            for w_option in json_arr:
                logging.info('Insert %s => %s on site #%d',
                    w_option['name'], w_option['data'], w_option['website_id'])
                bulk_arr.append(WebsiteOption(
                    website_id=w_option['website_id'],
                    name=w_option['name'],
                    data=w_option['data']['data']
                ))

            WebsiteOption.objects.bulk_create(bulk_arr)
