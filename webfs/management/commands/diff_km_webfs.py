import re
import os
from collections import deque
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from knowledge_map.models import ManagedFile as KMManagedFile
from webfs.models import ManagedFile as WebFSManagedFile


# python3 manage.py diff_km_webfs
class Command(BaseCommand):
    help = 'Diff KM and WebFS'

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        for file in KMManagedFile.objects.select_related('unique_file').order_by('id'):
            try:
                WebFSManagedFile.objects.get(id=file.id)
            except WebFSManagedFile.DoesNotExist:
                uf = file.unique_file
                msg = f'{file.original_path}({file.id}) - {uf.name}{uf.content_type} not found.'
                self.stdout.write(self.style.ERROR(msg))



