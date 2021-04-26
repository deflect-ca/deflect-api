from django.db import models


class Edge(models.Model):
    class Meta:
        app_label = "api"

    id = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=255, null=False)
    ip = models.CharField(max_length=16, null=False)
    dnet = models.ForeignKey('Dnet',
        on_delete=models.CASCADE, related_name='dnets')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __repr__(self):
        return '<edge id={}, hostname={}>'.format(
            self.id, self.hostname)

    def __str__(self):
        return '<edge id={}, hostname={}>'.format(
            self.id, self.hostname)
