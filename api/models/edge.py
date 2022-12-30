import logging

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from api.modules.edgemanage import update_dnet_edges

logger = logging.getLogger(__name__)


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

    @staticmethod
    def post_save(**kwargs):
        """
        Edge list updated
        1. update edgemanage files
        """
        logging.debug(kwargs)
        update_dnet_edges(Edge.get_mapping())

    @staticmethod
    def post_delete(**kwargs):
        """
        Edge deleted
        1. update edgemanage files
        2. ? (TODO)
        """
        logging.debug(kwargs)
        update_dnet_edges(Edge.get_mapping())

    @staticmethod
    def get_mapping():
        mapping = {}
        edges = Edge.objects.only('dnet')  # lazyload dnets
        for edge in edges:
            dnet = edge.dnet.name
            if dnet in mapping:
                mapping[dnet].append(edge.hostname)
            else:
                mapping[dnet] = [edge.hostname]
        return mapping

    def __repr__(self):
        return '<edge id={}, hostname={}>'.format(
            self.id, self.hostname)

    def __str__(self):
        return '<edge id={}, hostname={}>'.format(
            self.id, self.hostname)


post_save.connect(Edge.post_save, sender=Edge)
post_delete.connect(Edge.post_delete, sender=Edge)
