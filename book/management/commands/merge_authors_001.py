import re
import os
import glob
import json
import sqlite3
from django.core.management.base import BaseCommand
from global_utils.publishers import ptpress_tags


def has_chinese_str(s):
    for char in s:
        if 0x4e00 < ord(char) < 0x9fff:
            return True
    return False


# python3 manage.py merge_authors_001 --src-db data/ptpress_book_authors.db --dst-db data/ptpress_authors_001.db
class Command(BaseCommand):
    help = 'Load all authors'

    def __init__(self):
        super().__init__()
        self.src_dbfile = "no exist dbfile"
        self.dst_dbfile = "no exist dbfile"

    def add_arguments(self, parser):
        parser.add_argument('--src-db', type=str, help="source database file")
        parser.add_argument('--dst-db', type=str, help="target database file")

    def init_and_check(self, options):
        self.src_dbfile = options['src_db']
        self.dst_dbfile = options['dst_db']

        if not os.path.isfile(self.src_dbfile):
            self.stdout.write(self.style.ERROR(f'source database {self.src_dbfile} file not exists'))
            return False

        if os.path.isfile(self.dst_dbfile):
            self.stdout.write(self.style.ERROR(f'target database {self.dst_dbfile} file already exists'))
            return False

        with sqlite3.connect(self.dst_dbfile) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS author(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT NOT NULL,
                    origin_text TEXT,
                    author TEXT,
                    alias TEXT,
                    country TEXT,
                    author_revision TEXT,
                    alias_revision TEXT,
                    country_revision TEXT,
                    status INTEGER
                )
            ''')
            conn.commit()

        return True

    def handle(self, *args, **options):
        if not self.init_and_check(options):
            return

        origin_rows = []
        with sqlite3.connect(self.src_dbfile) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM author WHERE status != 2')
                for row in cursor.fetchall():
                    origin_rows.append(row)
            finally:
                cursor.close()

        target_rows = []
        for row in origin_rows:
            _id, isbn, origin_text, author, alias, country, author_rev, alias_rev, country_rev, status = row
            if not (country_rev.startswith('日') or country_rev.startswith('韩')
                    or country_rev.startswith('新') or country_rev.startswith('马')):
                if alias_rev and len(alias_rev) > 0:
                    if has_chinese_str(author_rev) and not has_chinese_str(alias_rev):
                        author_rev, alias_rev = alias_rev, author_rev

            target_rows.append((isbn, origin_text, author, alias, country, author_rev, alias_rev, country_rev, status))

        sql = '''INSERT INTO author(`isbn`, `origin_text`, `author`, `alias`, `country`, `author_revision`, 
            `alias_revision`, `country_revision`, `status`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        with sqlite3.connect(self.dst_dbfile) as conn:
            cursor = conn.cursor()
            try:
                for row in sorted(target_rows, key=lambda x: x[5]):
                    cursor.execute(sql, row)
                conn.commit()
            finally:
                cursor.close()






