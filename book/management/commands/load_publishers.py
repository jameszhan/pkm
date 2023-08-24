import re
import os
import mimetypes
from django.core.management.base import BaseCommand
from book.models import Publisher


# python3 manage.py load_publishers --mdfile data/publishers.md
class Command(BaseCommand):
    help = 'Load all publishers'

    def add_arguments(self, parser):
        parser.add_argument('--mdfile', type=str, help="markdown table file")

    def handle(self, *args, **options):
        mdfile = options['mdfile']
        if not os.path.isfile(mdfile):
            self.stdout.write(self.style.ERROR(f'file not exists, path {mdfile}'))
            return

        pattern = r'\|\s*(7\-\d+)\s*\|([^|]+)\|([^|]+)\|\s*(\d{3})\s*\|'
        with open(mdfile, 'r', encoding='UTF-8') as f:
            for line in f:
                m = re.match(pattern, line)
                if m:
                    obj, created = Publisher.objects.update_or_create(isbn=m.group(1), defaults={
                        'name': m.group(2),
                        'addr': m.group(3),
                        'code': m.group(4),
                    })
                    self.stdout.write(self.style.SUCCESS(f'{obj} created {created}'))


