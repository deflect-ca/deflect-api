import logging

from rest_framework import serializers
from api.models import Record

logger = logging.getLogger(__name__)


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = ['id', 'type', 'hostname', 'value', 'priority', 'weight', 'port', 'ttl']
