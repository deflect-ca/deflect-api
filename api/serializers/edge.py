from rest_framework import serializers
from api.models import Edge


class EdgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Edge
        fields = ['id', 'hostname', 'ip', 'dnet', 'created_at', 'updated_at']
