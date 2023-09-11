import os
import json
from datetime import datetime
import sqlite3
from django.core.management.base import BaseCommand
from global_utils.publishers import ptpress_mapping
from global_utils.country_codes import country_codes
from book.models import Publisher, Author, Category, Book


def normalize_isbn(origin_isbn):
    if origin_isbn.startswith('978'):
        return origin_isbn.replace('-', '')
    else:
        return '978' + origin_isbn.replace('-', '')


# python3 manage.py load_books --sqlite data/ptpress.db --publisher 7-115
class Command(BaseCommand):
    help = 'Load all books'

    def add_arguments(self, parser):
        parser.add_argument('--sqlite', type=str, help="database file")
        parser.add_argument('--publisher', type=str, help="publisher isbn code")

    def handle(self, *args, **options):
        dbfile = options['sqlite']
        if not os.path.isfile(dbfile):
            self.stdout.write(self.style.ERROR(f'file not exists, path {dbfile}'))
            return

        publisher_isbn = options['publisher']
        try:
            publisher = Publisher.objects.get(isbn=publisher_isbn)
        except Publisher.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'publisher not exists, isbn: {publisher_isbn}'))
            return

        self.stdout.write(self.style.SUCCESS(f'publisher found: {publisher}'))

        book_author_selectors = {}
        with sqlite3.connect(dbfile) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM book_author')
            for row in cursor.fetchall():
                _, isbn, author, alias, country, _ = row
                isbn = normalize_isbn(isbn)
                if isbn not in book_author_selectors:
                    book_author_selectors[isbn] = []

                if alias is None:
                    alias = ''
                nationality = country_codes[country]
                book_author_selectors[isbn].append((author.strip(), nationality, alias.strip()))

        author_cache = {}
        category_cache = {}
        books = {}
        with sqlite3.connect(dbfile) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM book')
                for row in cursor.fetchall():
                    _, _, category, isbn, title, author, pic, publish_date, executive_editor, stock_in_date, price, book_code, book_id, sum_volume, shop_type = row
                    info = {
                        "category": category,
                        "isbn": isbn,
                        "name": title,
                        "author": author,
                        "pic": pic,
                        "publish_date": publish_date,
                        "executive_editor": executive_editor,
                        "stock_in_date": stock_in_date,
                        "price": price,
                        "book_code": book_code,
                        "book_id": book_id,
                        "sum_volume": sum_volume,
                        "shop_type": shop_type
                    }
                    if isbn.startswith('978'):
                        isbn = isbn.replace('-', '')
                    else:
                        isbn = '978' + isbn.replace('-', '')

                    if isbn not in books:
                        books[isbn] = info
                        category_name = ptpress_mapping[category]
                        if category_name in category_cache:
                            cat = category_cache[category_name]
                        else:
                            cat = Category.objects.get(name=category_name)
                            category_cache[category_name] = cat

                        book, created = Book.objects.get_or_create(isbn=isbn, version='', defaults={
                            "title": title,
                            "publisher": publisher,
                            "cover_image": pic,
                            "publication_date":  datetime.strptime(publish_date, "%Y%m").date(),
                            "extra": info
                        })
                        if created:
                            if isbn in book_author_selectors:
                                authors = []
                                for author_name, country, alias in book_author_selectors[isbn]:
                                    if (author_name, country, alias) in author_cache:
                                        author = author_cache[(author_name, country, alias)]
                                    else:
                                        author = Author.objects.get(name=author_name, nationality=country, descriptor=alias)
                                        author_cache[(author_name, country, alias)] = author
                                    authors.append(author)
                                book.authors.set(authors)
                            book.categories.add(cat)
                        self.stdout.write(self.style.SUCCESS(f'{"忽略" if created else "创建"} {isbn}-{book.id}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'忽略重复图书: {info}'))
            finally:
                cursor.close()



