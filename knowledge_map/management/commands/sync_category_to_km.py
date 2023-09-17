import re
import os
from collections import deque
from django.core.management.base import BaseCommand
from django.db import connection
from book.models import Category
from knowledge_map.models import Category as KMCategory


# python3 manage.py sync_category_to_km
class Command(BaseCommand):
    help = 'Sync All Categories'

    def handle(self, *args, **options):
        km_catalogs = {}
        for category in Category.objects.prefetch_related('parent').order_by('id'):
            r, created = KMCategory.objects.get_or_create(id=category.id,
                                                          slug=category.slug,
                                                          name=category.name,
                                                          topic=category.topic)
            self.stdout.write(self.style.SUCCESS(f'{"创建" if created else "忽略"} {r.name}({r.slug}-{r.id})'))
            km_catalogs[r.slug] = r

            if category.parent is not None and category.parent.slug in km_catalogs:
                r.parents.create(parent=km_catalogs[category.parent.slug])
                self.stdout.write(self.style.SUCCESS(f'创建关系 {r.slug} <- {category.parent.slug}'))











