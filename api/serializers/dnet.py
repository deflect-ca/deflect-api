from rest_framework import serializers
from api.models import Dnet


class DnetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dnet
        fields = ['id', 'name', 'created_at', 'updated_at']
