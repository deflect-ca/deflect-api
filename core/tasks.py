from celery import shared_task
from django.core.management import call_command


@shared_task
def gen_site_config_task():
    call_command('gen_site_config')
