import logging
import json

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

from api.modules.util import CustomSchema
from api.modules.edgemanage import edge_query, edge_conf, dnet_query


logger = logging.getLogger(__name__)


class Edge(APIView):
    schema = CustomSchema(tags=['edgemanage'], load_api_yaml=True)

    def get(self, request):
        """ List all edges managed by edgemanage """
        try:
            return Response(edge_query(request.GET['dnet']))
        except KeyError as err:
            logger.error(err)
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            logger.error(err)
            return Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Dnet(APIView):
    schema = CustomSchema(tags=['edgemanage'], load_api_yaml=True)

    def get(self, request):
        """ List all dnets managed by edgemanage """
        try:
            return Response(dnet_query())
        except FileNotFoundError as err:
            logger.error(err)
            return Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EdgeConf(APIView):
    schema = CustomSchema(tags=['edgemanage'], load_api_yaml=True)

    def put(self, request):
        """ Update edge config, put the edge in or out of rotation """
        try:
            edge_conf_result = edge_conf(
                request.data['dnet'], request.data['edge'],
                request.data['mode'], request.data['comment'],
                request.data['comment_user'])
            return Response(edge_conf_result, status=status.HTTP_201_CREATED)
        except KeyError as err:
            logger.error(err)
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            logger.error(err)
            return Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
