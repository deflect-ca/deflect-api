from celery import shared_task
from django.core.management import call_command
from django.conf import settings


@shared_task
def gen_site_config_task(_next=False, mode=None):
    call_command(
        'gen_site_config',
    )
