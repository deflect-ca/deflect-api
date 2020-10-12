from rest_framework import serializers
from api.models import WebsiteOption


class WebsiteOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WebsiteOption
        fields = ['name', 'data', 'id', 'website_id']
        read_only = ['id', 'website_id']
