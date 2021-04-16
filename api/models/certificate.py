from django.db import models
from django.db.models.signals import post_save
from api.modules.util import model_post_save


class Certificate(models.Model):
    class Meta:
        app_label = "api"

    # id = db.Column(db.Integer, primary_key=True)
    id = models.AutoField(primary_key=True)

    # hostnames = db.Column(db.Text(65000), nullable=False)
    hostnames = models.TextField(null=False)

    # fingerprint = db.Column(db.String(255), nullable=False)
    fingerprint = models.CharField(max_length=255, null=False)

    # has_private = db.Column(db.Boolean, default=False)
    has_private = models.BooleanField(default=False, null=True, blank=True)

    # The fingerprint of the issuing CA
    # issuing_ca = db.Column(db.String(255), nullable=False)
    issuing_ca = models.CharField(max_length=255, null=False)

    # date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    # date_expires = db.Column(db.DateTime)
    date_expires = models.DateTimeField(null=True, blank=True)

    # one-to-many with website
    # access website.certificates to get all options
    website = models.ForeignKey('Website',
        on_delete=models.CASCADE, related_name='certificates')

    def __repr__(self):
        return '<Certificate #{} {}>'.format(self.id, self.hostnames.split(", "))

    def __str__(self):
        return 'Certificate #{} {}'.format(self.id, self.hostnames.split(", "))

    @staticmethod
    def post_save(**kwargs):
        model_post_save(**kwargs)


post_save.connect(Certificate.post_save, sender=Certificate)
