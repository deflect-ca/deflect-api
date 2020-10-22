from django.db import transaction
from rest_framework import serializers
from api.models import Record
from .mixins import RecordValidationMixin


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = ['id', 'type', 'hostname', 'value', 'priority',
                  'weight', 'port', 'ttl']

class RecordCreateSerializer(serializers.ModelSerializer,
                             RecordValidationMixin):

    class Meta:
        model = Record
        fields = ['type', 'hostname', 'value', 'priority',
                  'weight', 'port', 'ttl', 'website_id']

    def __init__(self, *args, **kwargs):
        """
        Override default constructor
        remove website_id which will be used in save()
        (called from views.website)
        """
        self.website_id = kwargs.pop('website_id')
        super(RecordCreateSerializer, self).__init__(*args, **kwargs)

    @transaction.atomic
    def save(self, **kwargs):
        # Insert self.website_id to kwargs which will be merged with validated_data
        record = super(
            RecordCreateSerializer, self).save(website_id=self.website_id)
        self.record_validator(record)

class RecordModifySerializer(serializers.ModelSerializer,
                             RecordValidationMixin):

    class Meta:
        model = Record
        fields = ['type', 'hostname', 'value', 'priority',
                  'weight', 'port', 'ttl']

    @transaction.atomic
    def save(self, **kwargs):
        record = super(RecordModifySerializer, self).save()
        self.record_validator(record)
