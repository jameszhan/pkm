import re
import os
import glob
from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand
from book.models import Category


def extract_category(s):
    pattern = r"\-\s+\[\s+\]\s+([^(（]+)[(（]([^)）]+)"
    match = re.search(pattern, s)

    if match:
        chinese_name = match.group(1).strip()
        english_name = match.group(2).strip()
        return [chinese_name, english_name]
    else:
        return None

# python3 manage.py dbshell
# CREATE TABLE category_v0 SELECT * FROM category;


# python3 manage.py load_categories --cat-dir data/categories
class Command(BaseCommand):
    help = 'Load all categories'

    def add_arguments(self, parser):
        parser.add_argument('--cat-dir', type=str, help="load categories from directories")

    def handle(self, *args, **options):
        cat_dir = options['cat_dir']

        if not os.path.isdir(cat_dir):
            self.stdout.write(self.style.ERROR(f'categories directory {cat_dir} not exists'))
            return

        for file in glob.glob(f'{cat_dir}/*.md'):
            bn = os.path.basename(file)
            name, ext = os.path.splitext(bn)
            parent = Category.objects.get(slug=name)
            self.stdout.write(self.style.SUCCESS(f'Load file {bn} with parent slug {parent}'))

            with open(file, 'r', encoding='UTF-8') as f:
                for line in f:
                    val = extract_category(line)
                    if val:
                        cn, en = val
                        obj, created = Category.objects.get_or_create(slug=slugify(en), defaults={
                            "name": cn,
                            "parent": parent,
                            "created_by_id": 1,
                        })
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'{obj} 已创建'))
                        else:
                            self.stdout.write(self.style.WARNING(f'{obj} 已忽略'))












