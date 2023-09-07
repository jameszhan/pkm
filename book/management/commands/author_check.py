import re
import os
import glob
import json
import sqlite3
from django.core.management.base import BaseCommand
from global_utils.publishers import ptpress_tags


def sanitize_country(c):
    if c == '印':
        return '印度'
    elif c == '西':
        return '西班牙'
    elif c == '加':
        return '加拿大'
    elif c == '以':
        return '以色列'
    elif c == '挪':
        return '挪威'
    return c


# python3 manage.py author_check --src-db data/ptpress_authors_002.db
class Command(BaseCommand):
    help = 'Load all authors'

    def __init__(self):
        super().__init__()
        self.src_dbfile = "no exist dbfile"

    def add_arguments(self, parser):
        parser.add_argument('--src-db', type=str, help="source database file")

    def init_and_check(self, options):
        self.src_dbfile = options['src_db']

        if not os.path.isfile(self.src_dbfile):
            self.stdout.write(self.style.ERROR(f'source database {self.src_dbfile} file not exists'))
            return False

        return True

    def handle(self, *args, **options):
        if not self.init_and_check(options):
            return

        origin_rows = []
        with sqlite3.connect(self.src_dbfile) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM author ORDER BY author_revision')
                for row in cursor.fetchall():
                    origin_rows.append(row)
            finally:
                cursor.close()

        author_dict = {}
        alias_dict = {}
        target_rows = []
        for row in origin_rows:
            id_, isbn, origin_text, author, alias, country, author_rev, alias_rev, country_rev, status = row
            target_rows.append((author_rev.strip(), alias_rev, country_rev.strip(), isbn))
            author = author_rev.lower().strip()
            if author not in author_dict:
                if alias_rev:
                    author_dict[author] = (alias_rev, id_)
                    alias_dict[alias_rev.lower().strip()] = (author_rev, id_)
                else:
                    author_dict[author] = (None, id_)
            else:
                alias, id2 = author_dict[author]
                if alias != alias_rev:
                    print(author, alias, alias_rev, id_, id2)

        authors = {}
        for author, alias, country_, isbn in target_rows:
            country = sanitize_country(country_)
            if author not in authors:
                authors[author] = [alias, country, set()]
            else:
                c = authors[author][1]
                if country == '中':
                    continue

                if c != country:
                    if c == '中' or c == '美':
                        authors[author][1] = country
                    elif country == '美':
                        pass
                    else:
                        print(author, authors[author], country)
            authors[author][2].add(isbn)

        i = 0
        for author in sorted(authors):
            alias, country, isbns = authors[author]
            print(author, country, isbns)
            if i > 500:
                break
            i += 1















