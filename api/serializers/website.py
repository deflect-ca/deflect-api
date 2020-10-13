from rest_framework import serializers
from api.models import Website, WebsiteOption
from .website_options import WebsiteOptionSerializer


class WebsiteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        # without options in list
        fields = ['id', 'url', 'status', 'ip_address',
                  'hidden_domain', 'banjax_auth_hash',
                  'admin_key', 'under_attack', 'awstats_password',
                  'ats_purge_secret']
        read_only_fields = ['id', 'url']

class WebsiteSerializer(serializers.ModelSerializer):
    options = WebsiteOptionSerializer(many=True)
    hidden_domain = serializers.CharField(max_length=32, required=False)
    awstats_password = serializers.CharField(max_length=40, required=False)

    class Meta:
        model = Website
        fields = ['id', 'url', 'status', 'ip_address',
                  'hidden_domain', 'banjax_auth_hash',
                  'admin_key', 'under_attack', 'awstats_password',
                  'ats_purge_secret', 'options']
        read_only_fields = ['id', 'url']

    # Writable nested serializers
    def create(self, validated_data):
        options = validated_data.pop('options')
        website = Website.objects.create(**validated_data)
        for option in options:
            WebsiteOption.objects.create(website=website, **option)
        return website
