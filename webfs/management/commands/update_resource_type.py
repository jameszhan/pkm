import re
import os
from collections import deque
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from webfs.models import BaseUniqueFile, ManagedFile, PDFUniqueFile, EBookUniqueFile, Series


# python3 manage.py update_resource_type --keyword "books/archives/lectures/" --type "EDUCATIONAL_MATERIALS" --dry-run True
# python3 manage.py update_resource_type --keyword "favorites/manuals/" --type MANUALS --dry-run True
# python3 manage.py update_resource_type --keyword "favorites/notes/" --type NOTES --dry-run True
# python3 manage.py update_resource_type --keyword "favorites/papers/" --type PERIODICALS --dry-run True
# python3 manage.py update_resource_type --keyword "books/archives/papers/" --type PERIODICALS --dry-run True
# python3 manage.py update_resource_type --keyword "docs/papers/" --type PERIODICALS --dry-run True
# python3 manage.py update_resource_type --keyword "PDFs/magazines" --type PERIODICALS --dry-run True
# python3 manage.py update_resource_type --keyword "bookracks/journals/" --type PERIODICALS --dry-run True
# python3 manage.py update_resource_type --keyword "books/archives/originals/publications/" --type BOOKS --dry-run True
# python3 manage.py update_resource_type --keyword "memos/books/libraries/pdfs/" --type BOOKS --dry-run True
# python3 manage.py update_resource_type --keyword "books/bookracks/facsimiles/" --type BOOKS --dry-run True
# python3 manage.py update_resource_type --keyword "shared/ebooks/" --type BOOKS --dry-run True
# python3 manage.py update_resource_type --keyword "favorites/collections/" --type BOOKS --dry-run True
# python3 manage.py update_resource_type --keyword "slides/" --type SLIDES --dry-run True
# python3 manage.py update_resource_type --keyword QCon --type SLIDES --dry-run True
# python3 manage.py update_resource_type --keyword "qcon" --type SLIDES --dry-run True
class Command(BaseCommand):
    help = 'Sync Unique Files Series'

    def __init__(self):
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', type=bool, default=False, help="Dry Run")
        parser.add_argument('--keyword', type=str, help="Keyword")
        parser.add_argument('--type', type=str, help="Resource Type")

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        keyword = options['keyword']
        resource_type = options['type']

        type_choices = BaseUniqueFile.RESOURCE_TYPE_CHOICES
        found = False
        for value, label in type_choices:
            if value == resource_type:
                found = True
        if not found:
            self.stdout.write(self.style.ERROR(f'RESOURCE TYPE {resource_type} is invalid'))
            return

        self.stdout.write(self.style.WARNING(f'Update to {resource_type} by keyword {keyword}, dry-run: {dry_run}'))
        already_updated = set()
        for managed_file in ManagedFile.objects.prefetch_related('unique_file').filter(original_path__contains=keyword).order_by('id'):
            uf = managed_file.unique_file
            ct = ContentType.objects.get_for_model(uf).model
            global_id = f'{ct}-{uf.id}'
            if global_id in already_updated:
                self.stdout.write(self.style.WARNING(f'IGNORE UPDATE {global_id} {managed_file.original_path}@{uf.name} to {resource_type}'))
                continue
            if uf.resource_type == 'OTHER':
                if not dry_run:
                    update_fields = ['resource_type']
                    uf.resource_type = resource_type
                    if 'favorite' in keyword:
                        uf.storage_status = 'COLLECTED'
                        update_fields.append('storage_status')
                    uf.save(update_fields=update_fields)
                self.stdout.write(self.style.SUCCESS(f'UPDATE {global_id} {managed_file.original_path}@{uf.name} to {resource_type}'))
                already_updated.add(global_id)


