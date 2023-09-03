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


def extract_authors(s):
    pattern = r"[\[【［]([\u4e00-\u9fa5]+)[\]】］]\s*([^【】\[\]［］]+)"
    matches = re.findall(pattern, s)
    return matches


def extract_names(s):
    # 正则表达式匹配模式：中文字符和括号内的英文字符
    pattern = r"([^（(]+)[（(]([^）)]+)[）)]"
    match = re.search(pattern, s)

    if match:
        chinese_name = match.group(1).strip()
        english_name = match.group(2).strip()
        return [chinese_name, english_name]
    else:
        return None


def load_ptpress_authors(book, collector, ignores):
    author_str = book['author']

    author_str = remove_last_substring_if_match(author_str.strip(), '绘/编著')
    author_str = remove_last_substring_if_match(author_str.strip(), '著/绘')
    author_str = remove_last_substring_if_match(author_str.strip(), '著/摄影')
    author_str = remove_last_substring_if_match(author_str.strip(), '编著')
    author_str = remove_last_substring_if_match(author_str.strip(), '著')
    author_str = remove_last_substring_if_match(author_str.strip(), '主编')
    author_str = remove_last_substring_if_match(author_str.strip(), '编')
    author_str = remove_last_substring_if_match(author_str.strip(), '等')
    if '[' in author_str or '【' in author_str or '［' in author_str:
        if authors := extract_authors(author_str):
            for author in authors:
                country = author[0]
                author_text = author[1].strip()
                author_texts = []
                if '，' in author_text:
                    author_texts = author_text.split('，')
                if ',' in author_text:
                    author_texts = author_text.split(',')
                if '、' in author_text:
                    author_texts = author_text.split('、')
                if '；' in author_text:
                    author_texts = author_text.split('；')
                if '\u3000' in author_text:
                    author_texts = author_text.split('\u3000')

                if len(author_texts) > 0:
                    for a in author_texts:
                        key = (a.strip(), country)
                        if key not in collector:
                            collector[key] = []
                        collector[key].append(book)
                else:
                    key = (author_text, country)
                    if key not in collector:
                        collector[key] = []
                    collector[key].append(book)
        else:
            ignores.append(book)
    else:
        authors = author_str.strip().split()
        if len(authors) == 1:
            if '，' in author_str:
                authors = author_str.split('，')
            elif ',' in author_str:
                authors = author_str.split(',')
            elif '、' in author_str:
                authors = author_str.split('、')

        # for author in authors:
        #     if not is_chinese_str(author.strip()):
        #         ignores.append(book)
        #         return

        for author in authors:
            key = (author.strip(), '中')
            if key not in collector:
                collector[key] = []
            collector[key].append(book)


# python3 manage.py load_origin_books --publisher ptpress --dbfile data/ptpress_origin_books.db
class Command(BaseCommand):
    help = 'Load all books'

    def __init__(self):
        super().__init__()
        self.handlers = {
            'ptpress': load_ptpress_authors
        }
        self.dbfile = "data/origin_books.db"

    def add_arguments(self, parser):
        parser.add_argument('--publisher', type=str, help="publisher directory")
        parser.add_argument('--dbfile', type=str, help="sqlite database file")

    def init_sqlite_table(self):
        with sqlite3.connect(self.dbfile) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS book(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publisher_code TEXT NOT NULL,
                    category TEXT NOT NULL,
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
            c.execute('''
                CREATE TABLE IF NOT EXISTS author(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT NOT NULL,
                    origin_text TEXT,
                    author TEXT,
                    country TEXT,
                    alias TEXT,
                    status INTEGER
                )
            ''')
            conn.commit()

    def handle(self, *args, **options):
        publisher = options['publisher']
        pub_dir = f"data/{publisher}"
        if not os.path.isdir(pub_dir):
            self.stdout.write(self.style.ERROR(f'directory not exists, path {pub_dir}'))
            return
        self.dbfile = options['dbfile']
        if os.path.isfile(self.dbfile):
            self.stdout.write(self.style.INFO(f'dbfile {self.dbfile} has already exists'))
            return

        self.init_sqlite_table()

        with sqlite3.connect(self.dbfile) as conn:
            for file in glob.glob(f'{pub_dir}/*.jsonl'):
                bn = os.path.basename(file)
                name, ext = os.path.splitext(bn)
                category = ptpress_tags[name]
                cur = conn.cursor()
                with open(file, 'r', encoding='UTF-8') as f:
                    for line in f:
                        book = json.loads(line)
                        sql = '''INSERT INTO book(
                            `publisher_code`, `category`, `isbn`, `book_name`, `author`, `pic_path`, `publish_date`, 
                            `executive_editor`, `stock_in_date`, `price`, `book_code`, `book_id`, `sum_volume`, 
                            `shop_type`)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        '''
                        cur.execute(sql, (
                            publisher, category, book['isbn'], book['bookName'], book['author'], book['picPath'],
                            book['publishDate'], book['executiveEditor'],  book['stockInDate'], book['price'],
                            book['originBookCode'], book['bookId'], book['sumVolume'], book['shopType']))
                conn.commit()

        collector = {}
        ignores = []
        for file in glob.glob(f'{pub_dir}/*.jsonl'):
            with open(file, 'r', encoding='UTF-8') as f:
                for line in f:
                    book = json.loads(line)
                    if publisher in self.handlers:
                        self.handlers[publisher](book, collector, ignores)

        with sqlite3.connect(self.dbfile) as conn:
            cur = conn.cursor()
            for k in sorted(collector):
                sql = '''INSERT INTO author(`isbn`, `author`, `country`, `origin_text`, `alias`, `status`) 
                    VALUES (?, ?, ?, ?, ?, ?)
                '''
                author_name = k[0]
                alias = None
                names = extract_names(k[0])
                if names:
                    author_name, alias = names[0], names[1]
                origin_books = collector[k]
                if len(author_name.strip()) > 0:
                    for origin_book in origin_books:
                        cur.execute(sql, (origin_book['isbn'], author_name, k[1], origin_book['author'], alias, 1))
            conn.commit()

            cur = conn.cursor()
            for ignore_book in ignores:
                sql = '''INSERT INTO author(`isbn`, `origin_text`, `status`) VALUES (?, ?, ?)'''
                cur.execute(sql, (ignore_book['isbn'], ignore_book['author'], 0))
            conn.commit()



