import logging
import marshmallow

from django.db import transaction
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
        read_only_fields = ['id']

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
        read_only_fields = ['id']

    # Writable nested serializers
    @transaction.atomic
    def create(self, validated_data):
        options = validated_data.pop('options')
        website = Website.objects.create(**validated_data)

        for option in options:
            try:
                # Validate and create
                website.set_option(option['name'], option['data'])
            except marshmallow.ValidationError as err:
                # invoke transaction rollback
                raise serializers.ValidationError(str(err))

        return website

    # Updatable nested serializers
    @transaction.atomic
    def update(self, instance, validated_data):
        # pop options
        options = validated_data.pop('options')

        # call parent update function
        updated_instance = super(WebsiteSerializer, self).update(
            instance, validated_data)

        for option in options:
            try:
                # validate and create or update
                updated_instance.set_option(option['name'], option['data'])
            except marshmallow.ValidationError as err:
                # invoke transaction rollback
                raise serializers.ValidationError(str(err))

        return instance
