import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

from api.modules.util import CustomSchema
from core.tasks import gen_site_config_task

logger = logging.getLogger(__name__)


class GenSiteConfig(APIView):
    schema = CustomSchema(tags=['gen_site_config'])

    def get(self, request):
        async_id = gen_site_config_task.delay()
        return Response({"async_id": str(async_id)})
