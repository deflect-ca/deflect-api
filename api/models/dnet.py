import logging

from django.db import models
from django.db.models.signals import post_save, post_delete
from api.modules.edgemanage import update_dnet_edges

logger = logging.getLogger(__name__)


class Dnet(models.Model):
    class Meta:
        app_label = "api"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    @staticmethod
    def post_save(**kwargs):
        """
        Dnet list updated
        1. update edgemanage files
        """
        logging.debug(kwargs)
        update_dnet_edges(Dnet.get_mapping())

    @staticmethod
    def post_delete(**kwargs):
        """
        Dnet deleted
        1. update edgemanage files
        """
        logging.debug(kwargs)
        update_dnet_edges(Dnet.get_mapping())

    @staticmethod
    def get_mapping():
        from api.models import Edge
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
        return '<dnet id={}, name={}>'.format(
            self.id, self.name)

    def __str__(self):
        return '<dnet id={}, name={}>'.format(
            self.id, self.name)


post_save.connect(Dnet.post_save, sender=Dnet)
post_delete.connect(Dnet.post_delete, sender=Dnet)
