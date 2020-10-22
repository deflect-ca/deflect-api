import logging

from rest_framework import serializers
from api.modules.dns import DNSUtils, InvalidZoneFile
from api.models import Record

logger = logging.getLogger(__name__)


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = ['id', 'type', 'hostname', 'value', 'priority',
                  'weight', 'port', 'ttl']

class RecordCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = ['id', 'type', 'hostname', 'value', 'priority',
                  'weight', 'port', 'ttl', 'website_id']

    def __init__(self, *args, **kwargs):
        """
        Override default constructor
        remove website_id which will be used in save()
        """
        self.website_id = kwargs.pop('website_id')
        super(RecordCreateSerializer, self).__init__(*args, **kwargs)

    def save(self, **kwargs):
        # Insert self.website_id to kwargs which will be merged with validated_data
        record = super(
            RecordCreateSerializer, self).save(website_id=self.website_id)
        website = record.website
        records = website.records.all()

        try:
            # insert new record
            dns_util = DNSUtils()
            dns_util.create_and_validate_zone_file(website, records)
        except InvalidZoneFile as err:
            # Rollback new record, return validation errors to the user.
            raise serializers.ValidationError(str(err))
