import os
import hashlib
import mimetypes
from datetime import datetime, timezone
import fitz
from django.db import transaction
from django.core.management.base import BaseCommand
from knowledge_map.models import UniqueFile, ManagedFile


TARGET_ROOT = f'/opt/rootfs/pkm'


# python3 manage.py sanitize_filename
class Command(BaseCommand):
    help = 'Sanitize filenames'

    def __init__(self):
        super().__init__()

    def handle(self, *args, **kwargs):
        files = ManagedFile.objects.filter(original_path__startswith='books/archives/originals//')
        for file in files:
            new_original_path = file.original_path.replace('//', '/')
            self.stdout.write(self.style.SUCCESS(f'Change filepath from {file.original_path} to {new_original_path}'))
            file.original_path = new_original_path
            file.save()


