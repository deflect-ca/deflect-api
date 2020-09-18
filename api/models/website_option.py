from django.db import models
from django_mysql.models import JSONField, Model


class WebsiteOption(Model):
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
    data = models.JSONField(null=True)

    # one-to-many with website
    website = models.ForeignKey('Website', on_delete=models.CASCADE)