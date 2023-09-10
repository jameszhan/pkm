# Generated by Django 4.1.7 on 2023-09-10 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0007_catalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='parents',
            field=models.ManyToManyField(blank=True, related_name='children', to='book.catalog'),
        ),
    ]
