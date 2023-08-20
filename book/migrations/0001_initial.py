# Generated by Django 4.1.7 on 2023-08-19 20:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('aliases', models.JSONField(blank=True, null=True)),
                ('nationality', django_countries.fields.CountryField(max_length=2)),
            ],
            options={
                'db_table': 'author',
                'unique_together': {('name', 'nationality')},
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=200)),
                ('subtitle', models.CharField(blank=True, db_index=True, default='', max_length=200)),
                ('publication_date', models.DateField(db_index=True)),
                ('isbn', models.CharField(max_length=20, unique=True, verbose_name='ISBN')),
                ('rating', models.FloatField(blank=True, null=True)),
                ('publisher', models.CharField(blank=True, max_length=100, null=True)),
                ('cover_image', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('extra', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'book',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='book.category')),
            ],
            options={
                'db_table': 'category',
            },
        ),
        migrations.CreateModel(
            name='BookAuthor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('author', '原著'), ('translator', '翻译'), ('annotator', '校注')], max_length=10)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book.author')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book.book')),
            ],
            options={
                'db_table': 'book_authors',
                'unique_together': {('book', 'author', 'role')},
            },
        ),
        migrations.AddField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(through='book.BookAuthor', to='book.author'),
        ),
        migrations.AddField(
            model_name='book',
            name='categories',
            field=models.ManyToManyField(related_name='books', to='book.category'),
        ),
        migrations.AddField(
            model_name='book',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
