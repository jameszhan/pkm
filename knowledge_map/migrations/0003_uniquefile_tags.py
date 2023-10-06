# Generated by Django 4.1.7 on 2023-09-26 17:48

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('knowledge_map', '0002_alter_uniquefile_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='uniquefile',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
