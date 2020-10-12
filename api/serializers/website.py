from rest_framework import serializers
from api.models import Website
from .website_options import WebsiteOptionSerializer


class WebsiteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        # without options in list
        fields = ['id', 'url', 'status', 'ip_address',
                  'hidden_domain', 'banjax_auth_hash',
                  'admin_key', 'under_attack', 'awstats_password',
                  'ats_purge_secret']
        read_only = ['id', 'url']

class WebsiteSerializer(serializers.ModelSerializer):
    options = WebsiteOptionSerializer(many=True)

    class Meta:
        model = Website
        fields = ['id', 'url', 'status', 'ip_address',
                  'hidden_domain', 'banjax_auth_hash',
                  'admin_key', 'under_attack', 'awstats_password',
                  'ats_purge_secret', 'options']
        read_only = ['id', 'url']
