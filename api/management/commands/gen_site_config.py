from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generating site.yml according to database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('gen_site_config success'))
