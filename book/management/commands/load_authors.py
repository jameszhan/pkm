import json
import os
import sqlite3
from django.core.management.base import BaseCommand
from book.models import Author

country_codes = {
    "中": "CN",
    "丹": "DK",
    "丹麦": "DK",
    "乌克兰": "UA",
    "乌拉圭": "UY",
    "以色列": "IL",
    "伊朗": "IR",
    "俄": "RU",
    "俄罗斯": "RU",
    "保": "BG",
    "加拿大": "CA",
    "加纳": "GH",
    "匈牙利": "HU",
    "南非": "ZA",
    "印尼": "ID",
    "印度": "IN",
    "土": "TR",
    "土耳其": "TR",
    "埃": "EG",
    "埃及": "EG",
    "塞尔维亚": "RS",
    "塞浦": "CY",
    "墨": "MX",
    "奥": "AT",
    "奥地利": "AT",
    "孟加拉": "BD",
    "尼日利亚": "NG",
    "巴": "BR",
    "巴基": "PK",
    "巴西": "BR",
    "希": "GR",
    "希腊": "GR",
    "德": "DE",
    "意": "IT",
    "意大利": "IT",
    "挪威": "NO",
    "捷": "CZ",
    "摩洛哥": "MA",
    "斯洛伐克": "SK",
    "斯洛文尼亚": "SI",
    "斯里兰卡": "LK",
    "新": "SG",
    "新加坡": "SG",
    "新西": "NZ",
    "新西兰": "NZ",
    "日": "JP",
    "比": "BE",
    "比利时": "BE",
    "法": "FR",
    "波": "PL",
    "波兰": "PL",
    "泰": "TH",
    "澳": "AU",
    "澳大利亚": "AU",
    "爱": "IE",
    "爱尔兰": "IE",
    "瑞": "CH",
    "瑞典": "SE",
    "瑞士": "CH",
    "白俄罗斯": "BY",
    "罗": "RO",
    "罗马尼亚": "RO",
    "美": "US",
    "美国": "US",
    "芬": "FI",
    "苏": "RU",
    "英": "GB",
    "英国": "GB",
    "荷": "NL",
    "荷兰": "NL",
    "葡": "PT",
    "葡萄牙": "PT",
    "西班牙": "ES",
    "越": "VN",
    "阿根廷": "AR",
    "阿联酋": "AE",
    "韩": "KR",
    "马来": "MY",
    "马来西亚": "MY",
    "黑山共和国": "ME"
}


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







