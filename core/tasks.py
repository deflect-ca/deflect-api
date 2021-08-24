from celery import shared_task
from django.core.management import call_command
from django.conf import settings


@shared_task
def gen_site_config_task(_next=False, mode=None):
    call_command(
        'gen_site_config',
        next=_next,
        mode=mode
    )


@shared_task
def deflect_next_task(mode='full'):
    call_command(
        'deflect_next',
        config=settings.NEXT_CONFIG,
        nextconf=settings.NEXT_DN_CONFIG,
        sys=settings.NEXT_SYS_SITES,
        key=settings.NEXT_SSH_KEY,
        sites='dev/deflect_next_orchestration/input/current/old-sites.yml',
        mode=mode
    )
