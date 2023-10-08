import re
import os
from collections import deque
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from knowledge_map.models import UniqueFile
from webfs.models import ManagedFile, PDFUniqueFile, EBookUniqueFile, DocUniqueFile


# python3 manage.py sync_file_to_webfs
class Command(BaseCommand):
    help = 'Sync All Files'

    def __init__(self):
        super().__init__()
        self.model_types = {
            "application/pdf": PDFUniqueFile,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": DocUniqueFile,
            "application/vnd.ms-powerpoint": DocUniqueFile,
            "application/epub+zip": EBookUniqueFile,
            "application/vnd.ms-htmlhelp": EBookUniqueFile,
            "application/vnd.amazon.ebook": EBookUniqueFile,
            "application/x-mobipocket-ebook": EBookUniqueFile,
            "application/vnd.amazon.mobi8-ebook": EBookUniqueFile,
        }

    def handle(self, *args, **options):
        for unique_file in UniqueFile.objects.prefetch_related('managed_files').order_by('id'):
            mime = unique_file.content_type
            _, ext = os.path.splitext(unique_file.file_path)
            if mime in self.model_types:
                managed_files = unique_file.managed_files.all()
                model = self.model_types[mime]

                with transaction.atomic():
                    uf, created = model.objects.get_or_create(digest=unique_file.digest, defaults={
                        'file_path': unique_file.file_path,
                        'name': unique_file.name,
                        'extension': ext,
                        'content_type': unique_file.content_type,
                        'file_size': unique_file.file_size,
                        'created_time': unique_file.created_time,
                        'modified_time': unique_file.modified_time,
                        'accessed_time': unique_file.accessed_time,
                        'metadata': unique_file.metadata,
                    })
                    self.stdout.write(self.style.SUCCESS(f'{"创建" if created else "忽略"} {uf.name}{uf.extension}-{uf.id}'))
                    for managed_file in managed_files:
                        # ContentType.objects.get_for_model(uf),
                        mf, c = ManagedFile.objects.get_or_create(original_path=managed_file.original_path, defaults={
                            'id': managed_file.id,
                            'unique_file': uf,
                            'object_digest': uf.digest,
                        })
                        self.stdout.write(self.style.SUCCESS(f'{"创建" if c else "忽略"} {mf.original_path}-{mf.id}'))
            else:
                self.stdout.write(self.style.ERROR(f'({unique_file.name}{ext}) Content Type {mime} is not supported'))

