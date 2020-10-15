import logging
import marshmallow

from django.db import transaction
from rest_framework import serializers
from api.models import Website, WebsiteOption
from .website_options import WebsiteOptionSerializer
from .mixins import WebsiteValidationMixin

logger = logging.getLogger(__name__)


class WebsiteSerializer(serializers.ModelSerializer):
    """
    Most simple serializer with all fields
    Used in /list, /delete
    """
    class Meta:
        model = Website
        # without options in list
        fields = ['id', 'url', 'status', 'ip_address',
                  'hidden_domain', 'banjax_auth_hash',
                  'admin_key', 'under_attack', 'awstats_password',
                  'ats_purge_secret']
        read_only_fields = ['id', 'url']

class WebsiteDetailSerializer(serializers.ModelSerializer):
    """
    Most simple serializer + options
    Used in /<int:pk>
    """
    class Meta:
        model = Website
        # without options in list
        fields = ['id', 'url', 'status', 'ip_address',
                  'hidden_domain', 'banjax_auth_hash',
                  'admin_key', 'under_attack', 'awstats_password',
                  'ats_purge_secret', 'options']
        read_only_fields = ['id', 'url']

    # nested relations
    options = WebsiteOptionSerializer(many=True)

class WebsiteCreateSerializer(serializers.ModelSerializer,
                              WebsiteValidationMixin):
    """
    Create serializer with necessary fields only
    Used in /create
    """
    class Meta:
        model = Website
        # use default generated for:
        #   hidden_domain, awstats_password, ats_purge_secret
        fields = ['id', 'url', 'status', 'ip_address',
                  'banjax_auth_hash', 'admin_key', 'options']
        read_only_fields = ['id']

    # nested relations
    options = WebsiteOptionSerializer(many=True, required=False)

    # Writable nested serializers
    @transaction.atomic
    def create(self, validated_data):
        try:
            options = validated_data.pop('options')
            logger.debug(options)
        except KeyError:
            # no options in req
            logger.debug('empty options')
            options = []

        website = Website.objects.create(**validated_data)

        for option in options:
            try:
                # Validate and create
                website.set_option(option['name'], option['data'])
            except marshmallow.ValidationError as err:
                # invoke transaction rollback
                raise serializers.ValidationError(str(err))
            except KeyError as err:
                raise serializers.ValidationError("KeyError", str(err))

        return website

class WebsiteUpdateSerializer(serializers.ModelSerializer):
    """
    Update Serializer
    All fields is updatable, except id, url
    Used in /modify
    """
    class Meta:
        model = Website
        fields = ['id', 'url', 'status', 'ip_address',
                  'hidden_domain', 'banjax_auth_hash',
                  'admin_key', 'under_attack', 'awstats_password',
                  'ats_purge_secret', 'options']
        # Do not URL updates
        read_only_fields = ['id', 'url']

    # nested relations
    options = WebsiteOptionSerializer(many=True)

    # Updatable nested serializers
    @transaction.atomic
    def update(self, instance, validated_data):
        # pop options
        try:
            options = validated_data.pop('options')
            logger.debug(options)
        except KeyError:
            # no options in req
            logger.debug('Update #%d: No options in update', instance.id)
            options = []

        # call parent update function
        updated_instance = super(WebsiteUpdateSerializer, self).update(
            instance, validated_data)

        for option in options:
            try:
                # validate and create or update
                updated_instance.set_option(option['name'], option['data'])
            except marshmallow.ValidationError as err:
                # invoke transaction rollback
                raise serializers.ValidationError("Option schema error: %s" % str(err))
            except KeyError as err:
                raise serializers.ValidationError("KeyError: %s" % str(err))

        return updated_instance
