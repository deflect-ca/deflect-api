from django.db import models


class Record(models.Model):
    """
    Storing DNS record for a site
    """
    class Meta:
        app_label = "api"

    # id = db.Column(db.Integer, primary_key=True)
    id = models.AutoField(primary_key=True)

    # type = db.Column(db.String(6), nullable=False)
    type = models.CharField(max_length=6, null=False)

    # hostname = db.Column(db.String(255), nullable=False)
    hostname = models.CharField(max_length=255, null=False)

    # value = db.Column(db.Text(65000), nullable=False)
    value = models.TextField(null=False, default='')

    # priority = db.Column(db.Integer)
    priority = models.IntegerField(null=True, blank=True)

    # weight = db.Column(db.Integer)
    weight = models.IntegerField(null=True, blank=True)

    # website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    website = models.ForeignKey('Website',
        on_delete=models.CASCADE, related_name='records')

    # deflect = db.Column(db.Boolean, default=False, nullable=False)
    deflect = models.BooleanField(default=False, null=False)

    # port = db.Column(db.Integer, default=None)
    port = models.IntegerField(default=None, null=True, blank=True)

    # ttl = db.Column(db.Integer, default=3600)
    ttl = models.IntegerField(default=3600, null=True, blank=True)

    def __repr__(self):
        return '<Record id={}, type={}, hostname={}>'.format(
            self.id, self.type, self.hostname)

    def __str__(self):
        return 'Record id={}, type={}, hostname={}'.format(
            self.id, self.type, self.hostname)
