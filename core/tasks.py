from celery import shared_task
from django.core.management import call_command
from django.conf import settings


@shared_task
def gen_site_config_task():
    call_command('gen_site_config')


@shared_task
def deflect_next_task():
    call_command(
        'deflect_next',
        output=settings.NEXT_OUTPUT_PREFIX,
        config=settings.NEXT_CONFIG,
        sys=settings.NEXT_SYS_SITES,
        key=settings.NEXT_SSH_KEY,
        sites='dev/deflect_next/input/site-next4.yml'
    )