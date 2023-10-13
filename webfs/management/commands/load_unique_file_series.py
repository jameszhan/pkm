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
            print(managed_file.unique_file)
            if i > 10:
                break
            i += 1


        # for unique_file in UniqueFile.objects.order_by('id'):
        #     mime = unique_file.content_type
        #     _, ext = os.path.splitext(unique_file.file_path)
        #     if mime in self.model_types:
        #         managed_files = unique_file.managed_files.all()
        #         model = self.model_types[mime]
        #
        #         with transaction.atomic():
        #             uf, created = model.objects.get_or_create(digest=unique_file.digest, defaults={
        #                 'file_path': unique_file.file_path,
        #                 'name': unique_file.name,
        #                 'extension': ext,
        #                 'content_type': unique_file.content_type,
        #                 'file_size': unique_file.file_size,
        #                 'created_time': unique_file.created_time,
        #                 'modified_time': unique_file.modified_time,
        #                 'accessed_time': unique_file.accessed_time,
        #                 'metadata': unique_file.metadata,
        #             })
        #
        #             if not created:
        #                 updated_keys = []
        #                 if unique_file.created_time < uf.created_time:
        #                     uf.created_time = unique_file.created_time
        #                     updated_keys.append('created_time')
        #
        #                 if unique_file.modified_time < uf.modified_time:
        #                     uf.modified_time = unique_file.modified_time
        #                     updated_keys.append('modified_time')
        #
        #                 if updated_keys:
        #                     if uf.name != unique_file.name:
        #                         uf.name = unique_file.name
        #                         updated_keys.append('name')
        #
        #                     print(f'update file {uf.name} with keys {updated_keys}')
        #                     uf.save(update_fields=updated_keys)
        #
        #             self.stdout.write(self.style.SUCCESS(f'[UniqueFile] {"创建" if created else "忽略"} {uf.name}{uf.extension}-{uf.id}'))
        #             for managed_file in managed_files:
        #                 # ContentType.objects.get_for_model(uf),
        #                 mf, c = ManagedFile.objects.get_or_create(original_path=managed_file.original_path, defaults={
        #                     'id': managed_file.id,
        #                     'unique_file': uf,
        #                     'object_digest': uf.digest,
        #                 })
        #                 self.stdout.write(self.style.SUCCESS(f'[ManagedFile] {"创建" if c else "忽略"} {mf.original_path}-{mf.id}'))
        #     else:
        #         self.stdout.write(self.style.ERROR(f'({unique_file.name}{ext}) Content Type {mime} is not supported'))

