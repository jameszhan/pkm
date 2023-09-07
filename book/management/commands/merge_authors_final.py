import re
import os
import glob
import json
import sqlite3
from django.core.management.base import BaseCommand


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


# python3 manage.py merge_authors_final --src-db data/ptpress_authors_002.db --dst-db data/ptpress_authors.db
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
            try:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS author(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        author TEXT NOT NULL,
                        alias TEXT,
                        country TEXT NOT NULL,
                        isbns TEXT
                    )
                ''')
                c.execute('''
                    CREATE TABLE IF NOT EXISTS book_author(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        isbn TEXT NOT NULL,
                        author TEXT NOT NULL,
                        alias TEXT,
                        country TEXT NOT NULL,
                        origin_author TEXT
                    )
                ''')
                conn.commit()
            finally:
                c.close()
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
            target_rows.append((author_rev.strip(), alias_rev, country_rev.strip(), isbn, origin_text))
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
        book_authors = {}
        for author, alias, country_, isbn, origin_text in target_rows:
            if (isbn, author) not in book_authors:
                book_authors[(isbn, author)] = origin_text
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

        sql = 'INSERT INTO author(`author`, `alias`, `country`, `isbns`) VALUES(?, ?, ?, ?)'
        sql2 = 'INSERT INTO book_author(`isbn`, `author`, `alias`, `country`, `origin_author`) VALUES(?, ?, ?, ?, ?)'
        with sqlite3.connect(self.dst_dbfile) as conn:
            cursor = conn.cursor()
            # author_params = [(author, alias, country, isbns)
            #                  for author in sorted(authors)
            #                  for alias, country, isbns in [authors[author]]]
            author_params = [(author, authors[author][0], authors[author][1], json.dumps(list(authors[author][2])))
                             for author in sorted(authors)]
            cursor.executemany(sql, author_params)

            book_author_params = [(isbn, author, authors[author][0], authors[author][1], book_authors[(isbn, author)])
                                  for isbn, author in sorted(book_authors)]
            cursor.executemany(sql2, book_author_params)









