import re
import os
from collections import deque
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from webfs.models import ManagedFile, PDFUniqueFile, EBookUniqueFile, Series


# python3 manage.py load_unique_file_series
class Command(BaseCommand):
    help = 'Sync Unique Files Series'

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        series_map = {}
        for series in Series.objects.all():
            series_map[series.name] = series

        i = 0
        for managed_file in ManagedFile.objects.prefetch_related('unique_file').order_by('id'):
            for name, series in series_map.items():
                if name in managed_file.original_path:
                    uf = managed_file.unique_file
                    if uf.series is None:
                        updated_keys = ['series']
                        uf.series = series
                        if uf.resource_type == 'OTHER':
                            uf.resource_type = 'BOOKS'
                            updated_keys.append('resource_type')
                        if uf.status == 'DRAFT' or uf.status == 'LISTING':
                            uf.status = 'PUBLISHED'
                            updated_keys.append('status')
                        uf.save(update_fields=updated_keys)
                        self.stdout.write(self.style.SUCCESS(f'{uf} add to {series}'))
                    break

