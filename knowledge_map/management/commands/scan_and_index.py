import os
import hashlib
import mimetypes
from datetime import datetime, timezone
import fitz
from django.db import transaction
from django.core.management.base import BaseCommand
from knowledge_map.models import UniqueFile, ManagedFile


TARGET_ROOT = f'/opt/rootfs/pkm'


def sha256(filepath, block_size=4096):
    hash_fn = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(block_size), b""):
            hash_fn.update(byte_block)
    return hash_fn.hexdigest()


def process_pdf_file(foldername, filename, basename, root_dir, prefix):
    filepath = os.path.join(foldername, filename)
    sanitized_path = filepath.replace(root_dir, prefix)
    if ManagedFile.objects.filter(original_path=sanitized_path).exists():
        print(f'{filepath}({sanitized_path}) have already exists')
        return

    content_type, _ = mimetypes.guess_type(filepath)
    if content_type:
        digest = sha256(filepath)
        target_filepath = f'pdfs/{digest[:2] + "/" + digest[2:]}.pdf'
        stat = os.stat(filepath)
        with fitz.open(filepath) as pdf_document:
            metadata = pdf_document.metadata
            with transaction.atomic():
                # todo use st_birthtime replace st_ctime in Unix platform
                unique_file, created = UniqueFile.objects.update_or_create(
                    digest=digest,
                    defaults={
                        'name': basename,
                        'content_type': content_type,
                        'file_path': target_filepath,
                        'file_size': os.path.getsize(filepath),
                        'created_time': datetime.fromtimestamp(stat.st_ctime, timezone.utc),
                        'modified_time': datetime.fromtimestamp(stat.st_mtime, timezone.utc),
                        'accessed_time': datetime.fromtimestamp(stat.st_atime, timezone.utc),
                        'metadata': metadata,
                    }
                )

                managed_file = ManagedFile.objects.create(
                    original_path=sanitized_path,
                    file_type='.pdf',
                    unique_file=unique_file,
                )

                if created:
                    unique_filepath = os.path.join(TARGET_ROOT, target_filepath)
                    os.makedirs(os.path.dirname(unique_filepath), exist_ok=True)
                    os.rename(filepath, unique_filepath)
                    print(f'move file {managed_file.original_path} to {unique_file.file_path} successful')
                else:
                    os.remove(filepath)
                    print(f'remove file {managed_file.original_path} successful')


# python3 manage.py scan_and_index --directories data/rootfs/directories.md
class Command(BaseCommand):
    help = 'Scan and index local files'

    def __init__(self):
        super().__init__()
        self.processors = {
            '.pdf': process_pdf_file
        }

    def add_arguments(self, parser):
        parser.add_argument('--directories', type=str, help="directories.md file")

    def handle(self, *args, **kwargs):
        directories_file = kwargs['directories']

        if not os.path.isfile(directories_file):
            self.stdout.write(self.style.ERROR(f'directories {directories_file} not exists'))
            return

        directories = {}
        with open(directories_file, 'r', encoding='UTF-8') as f:
            for line in f:
                root_dir, prefix = [s.strip() for s in line.split(':', 1)]
                directories[root_dir] = prefix

        for root_dir, prefix in directories.items():
            for foldername, subfolders, filenames in os.walk(root_dir):
                subfolders[:] = [s for s in subfolders if not s.startswith('.')]
                filenames[:] = [f for f in filenames if not f.startswith('.')]
                for filename in filenames:
                    basename, ext = os.path.splitext(filename)
                    if ext in self.processors:
                        self.processors[ext](foldername, filename, basename, root_dir, prefix)

