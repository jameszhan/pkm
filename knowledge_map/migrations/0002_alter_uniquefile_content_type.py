# Generated by Django 4.1.7 on 2023-09-26 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge_map', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uniquefile',
            name='content_type',
            field=models.CharField(db_index=True, max_length=32),
        ),
    ]
