import re
import os
import glob
import json
import sqlite3
import mimetypes
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


def load_ptpress_authors(book, collector, rest):
    author_str = book['author']
    if '[' in author_str or '【' in author_str or '［' in author_str or '(' in author_str or '（' in author_str:
        rest.write(f'{json.dumps(book, ensure_ascii=False)}\n')
    else:
        author_str = remove_last_substring_if_match(author_str.strip(), '编著')
        author_str = remove_last_substring_if_match(author_str.strip(), '著')
        author_str = remove_last_substring_if_match(author_str.strip(), '主编')
        author_str = remove_last_substring_if_match(author_str.strip(), '等')
        authors = author_str.split()
        if len(authors) == 1:
            if '，' in author_str:
                authors = author_str.split('，')
            elif ',' in author_str:
                authors = author_str.split(',')
            elif '、' in author_str:
                authors = author_str.split('、')

        for author in authors:
            if not is_chinese_str(author):
                rest.write(f'{json.dumps(book, ensure_ascii=False)}\n')
                return

        for author in authors:
            if author not in collector:
                collector[author] = []
            collector[author].append(book['isbn'])


# python3 manage.py load_authors --publisher ptpress
class Command(BaseCommand):
    help = 'Load all authors'

    def __init__(self):
        super().__init__()
        self.handlers = {
            'ptpress': load_ptpress_authors
        }
        self.table_name = "data/books.db"
        self.init_sqlite_table()

    def add_arguments(self, parser):
        parser.add_argument('--publisher', type=str, help="publisher directory")

    def init_sqlite_table(self):
        with sqlite3.connect(self.table_name) as conn:
            with conn.cursor() as c:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS book(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        publisher_code TEXT NOT NULL,
                        isbn TEXT NOT NULL,
                        book_name TEXT,
                        author TEXT,
                        pic_path TEXT,
                        publish_date TEXT,
                        executive_editor TEXT,
                        stock_in_date TEXT,
                        price REAL,
                        book_code TEXT,
                        book_id TEXT,
                        sum_volume INTEGER,
                        shop_type INTEGER
                    )
                ''')
            conn.commit()

    def handle(self, *args, **options):
        publisher = options['publisher']
        pub_dir = f"data/{publisher}"
        if not os.path.isdir(pub_dir):
            self.stdout.write(self.style.ERROR(f'directory not exists, path {pub_dir}'))
            return

        with open('/tmp/authors.jsonl', 'w') as f1, open('/tmp/rest.jsonl', 'w') as f2:
            collector = {}
            for file in glob.glob(f'{pub_dir}/*.jsonl'):
                with open(file, 'r', encoding='UTF-8') as f:
                    for line in f:
                        book = json.loads(line)
                        if publisher in self.handlers:
                            self.handlers[publisher](book, collector, f2)

            for k in sorted(collector):
                f1.write(f'{json.dumps((k, collector[k]), ensure_ascii=False)}\n')



