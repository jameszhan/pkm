import json
import os
import sqlite3
from django.core.management.base import BaseCommand
from global_utils.country_codes import country_codes
from book.models import Author


# python3 manage.py load_authors --src-db data/ptpress_authors.db
class Command(BaseCommand):
    help = 'Load all authors'

    def add_arguments(self, parser):
        parser.add_argument('--src-db', type=str, help="authors sqlite database file")

    def handle(self, *args, **options):
        src_dbfile = options['src_db']

        if not os.path.isfile(src_dbfile):
            self.stdout.write(self.style.ERROR(f'source database {src_dbfile} file not exists'))
            return

        authors_by_countries = {}
        with sqlite3.connect(src_dbfile) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM author ORDER BY country')
            for row in cursor.fetchall():
                _, author, alias, country, _ = row
                if country in country_codes:
                    country_code = country_codes[country]
                    if country_code not in authors_by_countries:
                        authors_by_countries[country_code] = []
                    authors_by_countries[country_code].append((author, alias))
                else:
                    raise Exception(f'{country} not support')

        for country_code in sorted(authors_by_countries, reverse=True):
            for author, alias in authors_by_countries[country_code]:
                if alias:
                    record, created = Author.objects.get_or_create(name=author, nationality=country_code, aliases=[alias])
                else:
                    record, created = Author.objects.get_or_create(name=author, nationality=country_code)
                self.stdout.write(self.style.SUCCESS(f'{record} 被{"创建" if created else "忽略"}'))







