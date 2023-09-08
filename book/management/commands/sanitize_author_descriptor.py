import json
import os
import sqlite3
from django.core.management.base import BaseCommand
from book.models import Author


# python3 manage.py sanitize_author_descriptor
class Command(BaseCommand):
    help = 'Sanitize Author Descriptor'

    def handle(self, *args, **options):
        # target_authors = Author.objects.filter(aliases__isnull=False, descriptor__exact='')
        # for author in target_authors:
        #     print(author.aliases, type(author.aliases), len(author.aliases))
        #     if len(author.aliases) == 1:
        #         author.descriptor = author.aliases[0]
        #         author.save(update_fields=['descriptor'])

        target_authors = Author.objects.only('id', 'aliases', 'descriptor').filter(aliases__isnull=False,
                                                                                   descriptor__exact='')
        authors_to_update = []
        for author in target_authors:
            if len(author.aliases) == 1:
                author.descriptor = author.aliases[0]
                authors_to_update.append(author)
        updated_count = Author.objects.bulk_update(authors_to_update, ['descriptor'])
        self.stdout.write(self.style.SUCCESS(f'更新成功，数量：{updated_count}'))












