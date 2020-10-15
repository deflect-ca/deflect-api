import logging
import django

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

from api.modules.edgemanage import edge_query, edge_conf, dnet_query

logger = logging.getLogger(__name__)


@api_view(['GET'])
def api_info(request):
    return Response({
        'name': settings.APP_NAME,
        'debug': settings.DEBUG,
        'versions': {
            'django': django.get_version(),
        },
        'info': {
            'edgemanage_config': settings.EDGEMANAGE_CONFIG
        }
    })


@api_view(['GET'])
def api_edge_query(request):
    try:
        return Response(edge_query(request.GET['dnet']))
    except KeyError as err:
        logger.error(err)
        return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        logger.error(err)
        return Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def api_dnet_query(request):
    try:
        return Response(dnet_query())
    except FileNotFoundError as err:
        logger.error(err)
        return Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'GET'])
def api_edge_conf(request):
    if request.method == 'GET':
        # To display API run page
        return Response({})

    # request.method == 'POST':
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
