from rest_framework import serializers
from api.models import WebsiteOption
from rest_framework.validators import UniqueTogetherValidator


class WebsiteOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WebsiteOption
        fields = ['name', 'data']
