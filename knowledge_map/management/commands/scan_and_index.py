import os
import shutil
import hashlib
import mimetypes
import traceback
from datetime import datetime, timezone
import fitz
from django.db import transaction
from django.core.management.base import BaseCommand
from knowledge_map.models import UniqueFile, ManagedFile


TARGET_ROOT = os.getenv('FILE_ROOT', '/opt/rootfs/pkm')
mv_func = os.rename


def sha256(filepath, block_size=4096):
    hash_fn = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(block_size), b""):
            hash_fn.update(byte_block)
    return hash_fn.hexdigest()


def get_file_stats(filepath):
    stat = os.stat(filepath)
    created_time = datetime.fromtimestamp(stat.st_ctime, timezone.utc)
    if hasattr(stat, 'st_birthtime'):
        created_time = datetime.fromtimestamp(stat.st_birthtime, timezone.utc)
    modified_time = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
    accessed_time = datetime.fromtimestamp(stat.st_atime, timezone.utc)
    return created_time, modified_time, accessed_time, stat.st_size


def update_unique_file_if_needed(unique_file, created_time, modified_time, accessed_time, basename, file_size):
    updated_keys = []

    if created_time < unique_file.created_time or modified_time < unique_file.modified_time:
        if created_time < unique_file.created_time:
            unique_file.created_time = created_time
            updated_keys.append('created_time')

        if modified_time < unique_file.modified_time:
            unique_file.modified_time = modified_time
            updated_keys.append('modified_time')

        if accessed_time < unique_file.accessed_time:
            unique_file.accessed_time = accessed_time
            updated_keys.append('accessed_time')

        if basename != unique_file.name:
            unique_file.name = basename
            updated_keys.append('name')

        if file_size != unique_file.file_size:
            unique_file.file_size = file_size
            updated_keys.append('file_size')

        if updated_keys:
            unique_file.save(update_fields=updated_keys)

    return updated_keys


def get_pdf_metadata(filepath):
    with fitz.open(filepath) as pdf_document:
        return pdf_document.metadata


def process_common_file(foldername, filename, basename, root_dir, prefix, ext):
    catfolders = {
        ".ppt": "ppts",
        ".pps": "ppts",
        ".pptx": "ppts",
        ".chm": "chms",
        ".epub": "epubs",
        ".azw": "azws",
        ".azw3": "azws",
        ".mobi": "mobis"
    }

    if ext not in catfolders:
        print(f'{filename} not support, support extensions is {catfolders.keys()}')
        return

    filepath = os.path.join(foldername, filename)
    sanitized_path = filepath.replace(root_dir, prefix)
    if ManagedFile.objects.filter(original_path=sanitized_path).exists():
        print(f'{filepath}({sanitized_path}) have already exists')
        return

    content_type, _ = mimetypes.guess_type(filepath)
    if not content_type and ext == '.azw3':
        content_type = "application/vnd.amazon.mobi8-ebook"
    if content_type:
        with transaction.atomic():
            created_time, modified_time, accessed_time, file_size = get_file_stats(filepath)
            digest = sha256(filepath)
            catfolder = catfolders[ext]
            target_filepath = f'{catfolder}/{digest[:2]}/{digest[2:]}{ext}'

            unique_file, created = UniqueFile.objects.get_or_create(
                digest=digest,
                defaults={
                    'name': basename,
                    'content_type': content_type,
                    'file_path': target_filepath,
                    'file_size': file_size,
                    'created_time': created_time,
                    'modified_time': modified_time,
                    'accessed_time': accessed_time,
                    'metadata': '{}',
                }
            )
            if not created:
                updated_keys = update_unique_file_if_needed(unique_file, created_time, modified_time, accessed_time, basename, file_size)
                if updated_keys:
                    print(f'update file {unique_file.name} with keys {updated_keys}')
            else:
                print(f'create file {unique_file.name} with content-type {content_type} successful')

            managed_file = ManagedFile.objects.create(
                original_path=sanitized_path,
                file_type=ext,
                unique_file=unique_file,
            )

            if created:
                unique_filepath = os.path.join(TARGET_ROOT, target_filepath)
                os.makedirs(os.path.dirname(unique_filepath), exist_ok=True)
                mv_func(filepath, unique_filepath)
                print(f'move file {managed_file.original_path} to {unique_file.file_path} successful')
            else:
                os.remove(filepath)
                print(f'remove file {managed_file.original_path} successful')


def process_pdf_file(foldername, filename, basename, root_dir, prefix, ext):
    filepath = os.path.join(foldername, filename)
    sanitized_path = filepath.replace(root_dir, prefix)
    if ManagedFile.objects.filter(original_path=sanitized_path).exists():
        print(f'{filepath}({sanitized_path}) have already exists')
        return

    content_type, _ = mimetypes.guess_type(filepath)
    if content_type:
        with transaction.atomic():
            metadata = get_pdf_metadata(filepath)
            created_time, modified_time, accessed_time, file_size = get_file_stats(filepath)
            digest = sha256(filepath)
            target_filepath = f'pdfs/{digest[:2]}/{digest[2:]}.pdf'

            unique_file, created = UniqueFile.objects.get_or_create(
                digest=digest,
                defaults={
                    'name': basename,
                    'content_type': content_type,
                    'file_path': target_filepath,
                    'file_size': file_size,
                    'created_time': created_time,
                    'modified_time': modified_time,
                    'accessed_time': accessed_time,
                    'metadata': metadata,
                }
            )
            if not created:
                updated_keys = update_unique_file_if_needed(unique_file, created_time, modified_time, accessed_time, basename, file_size)
                if updated_keys:
                    print(f'update file {unique_file.name} with keys {updated_keys}')
            else:
                print(f'create file {unique_file.name} with content-type {content_type} successful')

            managed_file = ManagedFile.objects.create(
                original_path=sanitized_path,
                file_type='.pdf',
                unique_file=unique_file,
            )

            if created:
                unique_filepath = os.path.join(TARGET_ROOT, target_filepath)
                os.makedirs(os.path.dirname(unique_filepath), exist_ok=True)
                mv_func(filepath, unique_filepath)
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
            '.pdf': process_pdf_file,
            '.ppt': process_common_file,
            '.pptx': process_common_file,
            '.pps': process_common_file,
            '.epub': process_common_file,
            '.mobi': process_common_file,
            '.azw': process_common_file,
            '.azw3': process_common_file,
            '.chm': process_common_file
        }

    def add_arguments(self, parser):
        parser.add_argument('--directories', type=str, help="directories.md file")
        parser.add_argument('--mvfunc', type=str, help="shutil.move")

    def handle(self, *args, **kwargs):
        mv_func_arg = kwargs['mvfunc']
        if mv_func_arg == 'shutil.move':
            global mv_func
            mv_func = shutil.move

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
                    filepath = os.path.join(foldername, filename)
                    if os.path.islink(filepath):
                        continue

                    basename, ext = os.path.splitext(filename)
                    if ext in self.processors:
                        try:
                            self.processors[ext](foldername, filename, basename, root_dir, prefix, ext)
                        except (RuntimeError, ValueError):
                            err_msg = f'can`t process {os.path.join(foldername, filename)}, error: {traceback.format_exc()}'
                            self.stdout.write(self.style.ERROR(err_msg))



