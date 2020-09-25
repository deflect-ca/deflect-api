import base64
import uuid
import string
import random

from django.db import models


def generate_hidden_domain(domain_len=10):
    """
    Generate the random hidden domain for a website
    """
    return base64.b32encode(uuid.uuid4().bytes)[:domain_len].lower()


def generate_ats_purge_secret():
    """
    Generate the random ATS purge secret for a website
    """
    return ''.join(random.choice(
        string.ascii_lowercase + string.ascii_uppercase) for _ in range(16))


class Website(models.Model):
    """
    Model of website
    """
    class Meta:
        app_label = "api"

    id = models.AutoField(primary_key=True)

    # url = db.Column(db.String(255), unique=True, nullable=False)
    url = models.CharField(max_length=255, unique=True, null=False)

    # status = db.Column(db.Float, default=0, nullable=False)
    status = models.FloatField(default=0, null=False)

    # ip_address = db.Column(db.String(16))
    ip_address = models.CharField(max_length=16)

    # hidden_domain = db.Column(db.String(32), nullable=False, default=generate_hidden_domain)
    hidden_domain = models.CharField(max_length=32, null=False, default=generate_hidden_domain)

    # banjax_auth_hash = db.Column(db.String(255))
    banjax_auth_hash = models.CharField(max_length=255, null=True, blank=True)

    # admin_key = db.Column(db.String(255))
    admin_key = models.CharField(max_length=255, null=True, blank=True)

    # under_attack = db.Column(db.Integer, default=0)
    under_attack = models.BooleanField(default=False)

    # awstats_password = db.Column(db.String(40), nullable=False, default=lambda: uuid.uuid4())
    awstats_password = models.CharField(max_length=40, null=False, default=uuid.uuid4())

    # ats_purge_secret = \
    #     db.Column(db.String(64), default=lambda: ''.join(
    #         random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(16)))
    ats_purge_secret = \
        models.CharField(
            max_length=64, default=generate_ats_purge_secret, null=True, blank=True)

    # created = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def get_option(self, key, fallback=None):
        option = self.options.filter(name=key).first()
        if option is None and fallback is not None:
            return fallback
        elif option is None and fallback is None:
            return None
        return option.data.get('data')  # break json wrap

    def set_option(self, key, value):
        option = self.options.filter(name=key).first()
        data = {'data': value}  # wrap with json

        if option is None:
            return self.options.create(name=key, data=data)
        else:
            return option.update(data=data)

    def set_bulk_options(self, obj):
        for key in obj:
            self.set_option(key, obj[key])

    def list_option(self):
        all_options = self.options.all()
        dic = {}
        for options in all_options:
            dic[options.name] = options.data.get('data')
        return dic

    def __repr__(self):
        return '<Website #{} {}>'.format(self.id, self.url)
