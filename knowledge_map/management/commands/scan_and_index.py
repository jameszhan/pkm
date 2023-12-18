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
FALLBACK_MIMES = {
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.mobi': 'application/x-mobipocket-ebook',
    '.azw3': 'application/vnd.amazon.mobi8-ebook',
    '.epub': 'application/epub+zip',
    '.azw': 'application/vnd.amazon.ebook',
    '.chm': 'application/vnd.ms-htmlhelp',
    '.djvu': 'image/vnd.djvu',
    '.flv': 'video/x-flv',
    '.webp': 'image/webp',
}


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
    return created_time, modified_time, accessed_time, stat.st_size, stat.st_ino


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


def process_common_file(foldername, filename, basename, root_dir, prefix, ext, keep_origin_file):
    catfolders = {
        ".ppt": "ppts",
        ".pps": "ppts",
        ".pptx": "ppts",
        ".chm": "chms",
        ".epub": "epubs",
        ".azw": "azws",
        ".azw3": "azws",
        ".mobi": "mobis",
        ".djvu": "djvus",
        ".webp": "images",
        ".jpeg": "images",
        ".jpg": "images",
        ".bmp": "images",
        ".png": "images",
        ".gif": "images",
        ".mp3": "audio",
        ".mp4": "videos",
        ".flv": "videos",
    }

    if ext not in catfolders:
        print(f'{filename} not support, support extensions is {catfolders.keys()}')
        return

    filepath = os.path.join(foldername, filename)
    sanitized_path = filepath.replace(root_dir, prefix)
    managed_file = ManagedFile.objects.filter(original_path=sanitized_path).first()
    if managed_file is not None:
        digest = sha256(filepath)
        if digest == managed_file.unique_file_id:
            print(f'remove file {sanitized_path}({managed_file.unique_file_id}) successful')
            os.remove(filepath)
        else:
            print(f'[ERROR] {filepath}({sanitized_path}) have already exists, but not consistent')
        return

    content_type, _ = mimetypes.guess_type(filepath)
    if ext in FALLBACK_MIMES:
        content_type = FALLBACK_MIMES[ext]
    if content_type:
        do_save_fileinfo(content_type, filepath, basename, ext, catfolders[ext], sanitized_path, '{}', keep_origin_file)
    else:
        print(f'{filepath} can`t guess type, ext is {ext}')


def process_pdf_file(foldername, filename, basename, root_dir, prefix, ext, keep_origin_file):
    filepath = os.path.join(foldername, filename)
    sanitized_path = filepath.replace(root_dir, prefix)
    managed_file = ManagedFile.objects.select_related('unique_file').filter(original_path=sanitized_path).first()
    if managed_file is not None:
        digest = sha256(filepath)
        if digest == managed_file.unique_file.digest:
            print(f'remove file {sanitized_path}({managed_file.unique_file.digest}) successful')
            os.remove(filepath)
        else:
            print(f'[ERROR] {filepath}({managed_file.unique_file.file_size}-{os.stat(filepath).st_size}) have already exists, but not consistent')
        return

    content_type, _ = mimetypes.guess_type(filepath)
    if content_type:
        metadata = get_pdf_metadata(filepath)
        do_save_fileinfo(content_type, filepath, basename, ext, 'pdfs', sanitized_path, metadata, keep_origin_file)


def do_save_fileinfo(mimetype, filepath, basename, ext, catfolder, sanitized_path, metadata, keep_origin_file=False):
    with transaction.atomic():
        created_time, modified_time, accessed_time, file_size, src_inode = get_file_stats(filepath)
        digest = sha256(filepath)
        target_filepath = f'{catfolder}/{digest[:2]}/{digest[2:]}{ext}'

        unique_file, created = UniqueFile.objects.get_or_create(
            digest=digest,
            defaults={
                'name': basename,
                'content_type': mimetype,
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
            print(f'create file {unique_file.name} with content-type {mimetype} successful')

        if keep_origin_file:
            unique_filepath = os.path.join(TARGET_ROOT, target_filepath)
            if os.path.exists(unique_filepath):
                dst_inode = os.stat(unique_filepath).st_ino
                if src_inode != dst_inode:
                    if updated_keys:
                        os.unlink(unique_filepath)
                        os.link(filepath, unique_filepath)
                        print(f'link file {filepath} to {unique_filepath} successful')
                    else:
                        os.unlink(filepath)
                        os.link(unique_filepath, filepath)
                        print(f'link file {unique_filepath} to {filepath} successful')
            else:
                os.makedirs(os.path.dirname(unique_filepath), exist_ok=True)
                os.link(filepath, unique_filepath)
                print(f'link file {filepath} to {unique_filepath} successful')
        else:
            if created:
                unique_filepath = os.path.join(TARGET_ROOT, target_filepath)
                os.makedirs(os.path.dirname(unique_filepath), exist_ok=True)
                shutil.move(filepath, unique_filepath)
                print(f'move file {sanitized_path} to {unique_file.file_path} successful')
            else:
                os.remove(filepath)
                print(f'remove file {sanitized_path} successful')

        managed_file = ManagedFile.objects.create(
            original_path=sanitized_path,
            file_type=ext,
            unique_file=unique_file,
        )
        print(f'add managed file {managed_file.original_path} success')


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
            '.chm': process_common_file,
            '.webp': process_common_file,
            '.jpeg': process_common_file,
            '.jpg': process_common_file,
            '.png': process_common_file,
            '.gif': process_common_file,
            '.bmp': process_common_file,
            '.mp3': process_common_file,
            '.mp4': process_common_file,
            '.flv': process_common_file,
        }

    def add_arguments(self, parser):
        parser.add_argument('--directories', type=str, help="directories.md file")
        parser.add_argument('--keep-origin-file', type=bool, help="Keep Origin File")

    def handle(self, *args, **kwargs):
        directories_file = kwargs['directories']
        if not os.path.isfile(directories_file):
            self.stdout.write(self.style.ERROR(f'directories {directories_file} not exists'))
            return

        keep_origin_file = kwargs['keep_origin_file']

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
                            self.processors[ext](foldername, filename, basename, root_dir, prefix, ext, keep_origin_file)
                        except (RuntimeError, ValueError):
                            err_msg = f'can`t process {filepath}({os.stat(filepath).st_size}), error: {traceback.format_exc()}'
                            self.stdout.write(self.style.ERROR(err_msg))
                    # else:
                    #     if filename.endswith("djvu"):
                    #         self.stdout.write(self.style.WARNING(f'{ext} not support, filepath: {filepath}'))



