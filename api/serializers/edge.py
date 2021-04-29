from rest_framework import serializers
from api.models import Edge
from api.serializers import DnetSerializer


class EdgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Edge
        fields = ['id', 'hostname', 'ip', 'created_at', 'updated_at']
        read_only_fields = ['id']
