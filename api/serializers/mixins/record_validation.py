import logging

from rest_framework import serializers
from api.modules.dns import DNSUtils, InvalidZoneFile

logger = logging.getLogger(__name__)


class RecordValidationMixin():

    def record_validator(self, record):
        website = record.website
        records = website.records.all()

        try:
            # insert new record
            dns_util = DNSUtils()
            dns_util.create_and_validate_zone_file(website, records)
        except InvalidZoneFile as err:
            # Rollback new record, return validation errors to the user.
            logger.critical('Invalid zone! rollback triggered')
            raise serializers.ValidationError(str(err))
