from rest_framework import serializers
from api.models import Website


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ['id', 'url', 'status', 'ip_address',
                  'hidden_domain', 'banjax_auth_hash',
                  'admin_key', 'under_attack', 'awstats_password',
                  'ats_purge_secret']
