import logging
import yaml
import string
import os
import warnings

from django.conf import settings
from rest_framework.schemas.openapi import AutoSchema
from core.tasks import gen_site_config_task

logger = logging.getLogger(__name__)


class CustomSchema(AutoSchema):
    """
    AutoSchema subclass using schema_extra_info on the view.
    """
    def __init__(self, tags=None, load_api_yaml=False):
        self.op_id = None
        self.api_yaml = {}
        if load_api_yaml:
            current_path = os.path.dirname(os.path.realpath(__file__))
            with open(f"{current_path}/../../docs/api-descriptions.yml", 'r') as yml_file:
                self.api_yaml = yaml.load(yml_file, Loader=yaml.FullLoader)
        super().__init__(tags=tags)

    def get_operation_id(self, path, method):
        self.op_id = super().get_operation_id(path, method)
        return self.op_id

    def get_responses(self, path, method):
        if self.op_id in self.api_yaml:
            return self.api_yaml[self.op_id]['responses']
        return super().get_responses(path, method)


def model_post_save(delete=False, **kwargs):
    """
    Sample kwargs: {
        'signal': <django.db.models.signals.ModelSignal object at 0x109ef34a8>,
        'sender': <class 'api.models.website.Website'>,
        'instance': <Website #39 example.com>,
        'created': True,
        'update_fields': None,
        'raw': False,
        'using': 'default'
    }
    """
    logger.debug(kwargs)

    if not settings.GSC_TRIGGER_UPON_DB_CHANGE:
        logger.info('GSC_TRIGGER_UPON_DB_CHANGE = False')
        return

    async_id = gen_site_config_task.delay()
    logger.info(f"Trigger task ID: {async_id}")
