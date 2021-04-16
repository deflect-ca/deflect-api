from django.db import models
from django_mysql.models import Model as DjangoMySQLModel
from marshmallow import fields, Schema, validate

from django.db.models.signals import post_save
from api.modules.util import model_post_save


class WebsiteOption(DjangoMySQLModel):
    """
    One website contains many website_option
    """
    class Meta:
        app_label = "api"

    # id = db.Column(db.Integer, primary_key=True)
    id = models.AutoField(primary_key=True)

    # name = db.Column(db.String(255), nullable=False)
    name = models.CharField(max_length=255, null=False)

    # data = db.Column(PickledDict, nullable=False)
    # An attempt to use JSON instead of Pickle
    data = models.JSONField(null=True, blank=True)

    # one-to-many with website
    # access website.options to get all options
    website = models.ForeignKey('Website',
        on_delete=models.CASCADE, related_name='options')

    def __repr__(self):
        return '<WebsiteOption {}={}>'.format(self.name, self.data)

    def __str__(self):
        return 'WebsiteOption {}={}'.format(self.name, self.data)

    @staticmethod
    def serialize(option_name, option_value):
        """
        Try to serialize a user supplied value based on the option schema

        Raises a validation error if the input is invalid
        """
        # this one acts differently than the others, but try to hide that here
        if option_name == "banjax_regex_banners":
            return BanjaxRegexBannersSchema().load(
                {'banners': option_value}).data['banners']
        else:
            schema = OptionSchema()
            return schema.load({option_name: option_value})

    def unserialize(self):
        """
        Unserialize an option based on the option schema
        """
        schema = OptionSchema()
        return schema.dump({self.name: self.data})

    @staticmethod
    def post_save(**kwargs):
        model_post_save(**kwargs)


class OptionSchema(Schema):
    """
    Types for serializing and validating custom website options
    """
    use_ssl = fields.Boolean(default=False)
    use_custom_ssl = fields.Boolean(default=False)
    enforce_valid_ssl = fields.Boolean(default=False)
    cert_issuer = fields.String(default='letsencrypt')
    https_option = fields.String(default='https_redirect')

    ssl_certificate_file_upload_date = fields.DateTime(default=None)
    ssl_key_file_upload_date = fields.DateTime(default=None)
    ssl_chain_file_upload_date = fields.DateTime(default=None)
    ssl_bundle_time = fields.Integer(default=None)
    ssl_origin = fields.Boolean(default=True)

    approved = fields.Boolean(default=False)
    save_visitor_logs = fields.Boolean(default=True)
    cache_time = fields.Integer(default=10)

    banjax_path = fields.List(fields.String, default=[])
    banjax_path_exceptions = fields.List(fields.String, default=[])

    banjax_sha_inv = fields.Boolean(default=False)
    banjax_captcha = fields.Boolean(default=False)

    additional_domain_prefix = fields.List(fields.String, default=[])
    add_banjax_whitelist = fields.List(fields.String, default=[])
    banjax_whitelist_include_auth = fields.Boolean(default=False)
    cache_exceptions = fields.List(fields.String, default=[])

    ns_last_email = fields.DateTime(default=None)
    ns_last_on_deflect = fields.DateTime(default=None)
    ns_on_deflect = fields.Boolean(default=True)
    ns_notifications_disabled = fields.Boolean(default=False)
    ns_monitoring_disabled = fields.Boolean(default=False)
    ns_unsubscribe_token = fields.String(default=None)

    inactive_pending_remove = fields.DateTime(default=None)
    inactive_whitelist = fields.Boolean(default=False)

    allow_http_delete_push = fields.Boolean(default=None)
    cachecontrol = fields.Boolean(default=None)
    cache_cookies = fields.Boolean(default=None)
    cachekey_param = fields.String(default=None)
    confremap = fields.Boolean(default=None)
    network = fields.String(default=None)
    no_www = fields.Boolean(default=None)
    origin_http_port = fields.Integer(default=None)
    origin_https_port = fields.Integer(default=None)
    origin_object = fields.String(default=None)
    www_only = fields.Boolean(default=None)


class BanjaxRegexBannerRegexSchema(Schema):
    """
    I don't think we can do a nested option like this in the same way the others
    are done. Maybe consider switching to one style? (ie. switch the others to
    this style?)
    """
    method = fields.String(required=True)
    ua = fields.String(required=True)
    url = fields.String(required=True)


class BanjaxRegexBannerSchema(Schema):
    """
    I can't figure out how to treat this one like OptionSchema.
    The nested validation stuff doesn't work right.
    """
    hits_per_interval = fields.Int(required=True)
    interval = fields.Int(required=True)
    regex = fields.Nested(BanjaxRegexBannerRegexSchema, required=True)


class BanjaxRegexBannersSchema(Schema):
    banners = fields.Nested(BanjaxRegexBannerSchema,
                            validate=validate.Length(min=1),
                            required=True, many=True)


post_save.connect(WebsiteOption.post_save, sender=WebsiteOption)
