from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from taggit.managers import TaggableManager


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    topic = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'category'


class Catalog(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    topic = models.TextField(null=True, blank=True)
    parents = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'catalog'


class Author(models.Model):
    name = models.CharField(max_length=200)
    aliases = models.JSONField(blank=True, null=True)
    nationality = CountryField()
    descriptor = models.CharField(max_length=200, default='')

    def __str__(self):
        descriptor_str = ""
        if self.descriptor:
            descriptor_str = "(" + self.descriptor + ")"

        return f'[{self.nationality}]{self.name}{descriptor_str}'

    class Meta:
        db_table = 'author'
        unique_together = ('name', 'nationality', 'descriptor')
        ordering = ('id',)


class Publisher(models.Model):
    isbn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=64, unique=True)
    addr = models.CharField(max_length=64, null=True, blank=True)
    code = models.CharField(max_length=64, null=True, blank=True, unique=True)
    alias = models.CharField(max_length=64, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'publisher'


class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    subtitle = models.CharField(max_length=200, default='', null=False, blank=True, db_index=True)
    authors = models.ManyToManyField(Author, through='BookAuthor')
    publication_date = models.DateField(db_index=True)
    isbn = models.CharField('ISBN', max_length=20)
    version = models.CharField(max_length=20, default='')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    rating = models.FloatField(null=True, blank=True)
    cover_image = models.URLField(null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name="books")
    description = models.TextField(null=True, blank=True)
    extra = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'book'
        unique_together = ('isbn', 'version')


AUTHOR_ROLES = [
    ('author', '原著'),
    ('translator', '翻译'),
    ('annotator', '校注'),
]


class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=AUTHOR_ROLES)

    class Meta:
        db_table = 'book_authors'
        unique_together = ('book', 'author', 'role')




