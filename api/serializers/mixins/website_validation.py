from django.core.validators import URLValidator, validate_ipv4_address
from django.core.exceptions import ValidationError
from rest_framework import serializers


class OptionalSchemeURLValidator(URLValidator):

    def __call__(self, value):
        if '://' not in value:
            # Validate as if it were http://
            value = 'http://' + value
        super(OptionalSchemeURLValidator, self).__call__(value)


class WebsiteValidationMixin():

    def validate_url(self, value):
        """
        Must be a valid URL
        """
        url_validator = OptionalSchemeURLValidator()

        try:
            url_validator(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid URL %s" % value)

        return value

    def validate_ip_address(self, value):
        """
        Must be a valid URL
        """
        try:
            validate_ipv4_address(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid IP %s" % value)

        return value
