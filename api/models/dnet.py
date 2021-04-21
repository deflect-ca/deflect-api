from django.db import models


class Dnet(models.Model):
    class Meta:
        app_label = "api"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __repr__(self):
        return '<dnet id={}, name={}>'.format(
            self.id, self.name)

    def __str__(self):
        return '<dnet id={}, name={}>'.format(
            self.id, self.name)
