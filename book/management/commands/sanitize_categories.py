import re
import os
from collections import deque
from django.core.management.base import BaseCommand
from django.db import connection
from book.models import Category

# CREATE TABLE old_category SELECT * FROM category;
# SET foreign_key_checks = 0;
# TRUNCATE TABLE category;
# SET foreign_key_checks = 1;


# python3 manage.py sanitize_categories
class Command(BaseCommand):
    help = 'Sanitize All Categories'

    def handle(self, *args, **options):
        categories_l1 = {
            '人文科学': 'humanities',
            '自然科学': 'natural-sciences',
            '数学': 'mathematics',
            '社会科学': 'social-sciences',
            '工程与技术': 'engineering-technology',
            '医学与健康': 'medicine-and-health',
            '商业与管理': 'business-management',
            '教育': 'education',
            '计算机科学': 'computer-science',
            '互联网': 'internet',
            '自我提升': 'self-improvement',
        }

        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE category_cte AS (
                    SELECT id, name, slug, topic, parent_id,  CAST(NULL AS CHAR(100)) AS parent_slug, created_by_id
                    FROM old_category
                    WHERE parent_id IS NULL
                    UNION ALL
                    SELECT c.id, c.name, c.slug, c.topic, c.parent_id, ct.slug AS parent_slug, c.created_by_id
                    FROM old_category AS c
                    JOIN category_cte AS ct ON c.parent_id = ct.id
                )
                SELECT id, name, slug, topic, parent_id, parent_slug, created_by_id 
                FROM category_cte ORDER BY parent_id, id;
            """)

            parent_category_map = {}
            for row in cursor.fetchall():
                _, name, slug, topic, _, parent_slug, _ = row
                if name not in categories_l1:
                    if parent_slug not in parent_category_map:
                        parent_category_map[parent_slug] = []
                    parent_category_map[parent_slug].append((name, slug, topic))

            queue = deque()
            category_ids = {}
            for n, s in categories_l1.items():
                r, created = Category.objects.get_or_create(slug=s, name=n, created_by_id=1)
                self.stdout.write(self.style.SUCCESS(f'{"创建" if created else "更新" } {n}({s}-{r.id}) 成功'))
                category_ids[s] = r.id
                queue.append(s)

            while queue:
                slug = queue.popleft()
                if slug in parent_category_map:
                    subcategories = parent_category_map[slug]
                    for (n, s, t) in subcategories:
                        r, created = Category.objects.get_or_create(slug=s,
                                                                    name=n,
                                                                    topic=t,
                                                                    parent_id=category_ids[slug],
                                                                    created_by_id=1)
                        self.stdout.write(self.style.SUCCESS(f'{"创建" if created else "更新"} {n}({s}-{r.id}) 成功'))
                        category_ids[s] = r.id
                        queue.append(s)



