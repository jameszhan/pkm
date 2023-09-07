import re
import os
import glob
import json
import sqlite3
from django.core.management.base import BaseCommand


def is_alpha(s):
    pattern = re.compile(r'^[A-Za-z]+$')
    return re.match(pattern, s)


# python3 manage.py merge_authors_002 --src-db data/ptpress_authors_001.db --dst-db data/ptpress_authors_002.db
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
            c.close()
            conn.commit()

        return True

    def handle(self, *args, **options):
        if not self.init_and_check(options):
            return

        origin_rows = []
        with sqlite3.connect(self.src_dbfile) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM author WHERE status != 2 ORDER BY id')
                for row in cursor.fetchall():
                    origin_rows.append(row)
            finally:
                cursor.close()

        author_dict = {}
        alias_dict = {}
        target_rows = []
        for row in origin_rows:
            id_, isbn, origin_text, author, alias, country, author_rev, alias_rev, country_rev, status = row
            target_rows.append(row[1:])
            author = author_rev.lower().strip()
            if author not in author_dict:
                if alias_rev:
                    author_dict[author] = (alias_rev, id_)
                    alias_dict[alias_rev.lower().strip()] = (author_rev, id_)
            else:
                alias, id2 = author_dict[author]
                if alias != alias_rev:
                    print(author, alias, alias_rev, id_, id2)

            # if is_alpha(author_rev.strip()):
            #     print(id_, author_rev, alias_rev)

        sql = '''INSERT INTO author(`isbn`, `origin_text`, `author`, `alias`, `country`, `author_revision`, 
                `alias_revision`, `country_revision`, `status`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        with sqlite3.connect(self.dst_dbfile) as conn:
            cursor = conn.cursor()
            try:
                for row in sorted(target_rows, key=lambda x: x[5]):
                    isbn, origin_text, author, alias, country, author_r, alias_r, country_r, status = row
                    params = (isbn, origin_text, author_r, alias_r, country_r, author_r, alias_r, country_r, status)
                    if status == 9:
                        for _ in range(5):
                            cursor.execute(sql, params)
                    else:
                        cursor.execute(sql, params)
                conn.commit()
            finally:
                cursor.close()










