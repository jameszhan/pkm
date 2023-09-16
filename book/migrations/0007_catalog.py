# Generated by Django 4.1.7 on 2023-09-10 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0006_category_topic_alter_book_publisher'),
    ]

    operations = [
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('topic', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parents', models.ManyToManyField(blank=True, related_name='subcatalogs', to='book.catalog')),
            ],
            options={
                'db_table': 'catalog',
            },
        ),
    ]