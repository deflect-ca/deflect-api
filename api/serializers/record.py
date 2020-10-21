import logging

from rest_framework import serializers
from api.models import Record

logger = logging.getLogger(__name__)


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = ['id', 'type', 'hostname', 'value', 'priority',
                  'weight', 'port', 'ttl']

class RecordCreateSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        """
        Override default constructor
        remove website_id which will be used in save()
        """
        self.website_id = kwargs.pop('website_id')
        super(RecordCreateSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Record
        fields = ['id', 'type', 'hostname', 'value', 'priority',
                  'weight', 'port', 'ttl', 'website_id']

    def save(self, **kwargs):
        # Insert self.website_id to kwargs which will be merged with validated_data
        super(RecordCreateSerializer, self).save(website_id=self.website_id)
