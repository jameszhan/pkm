import re
import os
from collections import deque
from django.core.management.base import BaseCommand
from django.db import connection
from book.models import Category, Catalog


# python3 manage.py sync_category_to_catalog
class Command(BaseCommand):
    help = 'Sanitize All Categories'

    def handle(self, *args, **options):
        catalogs = {}
        for category in Category.objects.prefetch_related('parent').order_by('id'):
            r, created = Catalog.objects.get_or_create(id=category.id,
                                                       slug=category.slug,
                                                       name=category.name,
                                                       topic=category.topic)
            self.stdout.write(self.style.SUCCESS(f'{"创建" if created else "忽略"} {r.name}({r.slug}-{r.id})'))
            catalogs[r.slug] = r

            if category.parent is not None and category.parent.slug in catalogs:
                r.parents.add(catalogs[category.parent.slug])
                self.stdout.write(self.style.SUCCESS(f'创建关系 {r.slug} <- {category.parent.slug}'))











