import re
import os
import glob
import json
import sqlite3
from django.core.management.base import BaseCommand
from global_utils.publishers import ptpress_tags


def is_chinese_str(s):
    for char in s:
        if ord(char) < 0x4e00 or ord(char) > 0x9fff:
            return False
    return True


def remove_last_substring_if_match(s, substring_to_remove="等"):
    if s.endswith(substring_to_remove):
        return s[:-len(substring_to_remove)]
    else:
        return s


# python3 manage.py sanitize_book_authors --src-db data/ptpress_origin_books.db --dst-db data/ptpress_book_authors.db
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
                cursor.execute('SELECT * FROM author')
                for row in cursor.fetchall():
                    origin_rows.append(row)
            finally:
                cursor.close()

        target_rows = []
        for row in origin_rows:
            _id, isbn, origin_text, author, country, alias, status = row
            author_revision = author
            alias_revision = alias
            if author.isascii() and alias and not alias.isascii():
                author_revision = alias
                alias_revision = author

            target_rows.append((isbn, origin_text, author, alias, country, author_revision, alias_revision, country, 0))

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

        # with sqlite3.connect(self.src_dbfile) as conn:
        #     cursor = conn.cursor()
        #
        #     page_size = 1000
        #     offset = 0
        #
        #     while True:
        #         cursor.execute(f'SELECT * FROM author LIMIT {page_size} OFFSET {offset}')
        #         rows = cursor.fetchall()
        #         if not rows:
        #             break
        #
        #         for row in rows:
        #             print(row)
        #
        #         offset += page_size
        #
        #     cursor.close()




