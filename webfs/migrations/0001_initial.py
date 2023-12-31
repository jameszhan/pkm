# Generated by Django 4.1.7 on 2023-10-08 18:26

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True, verbose_name='slug')),
                ('color', models.CharField(max_length=10, null=True)),
                ('metadata', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'File Tag',
                'verbose_name_plural': 'File Tags',
            },
        ),
        migrations.CreateModel(
            name='TaggedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(db_index=True, verbose_name='object ID')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_tagged_items', to='contenttypes.contenttype', verbose_name='content type')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_items', to='webfs.filetag')),
            ],
            options={
                'verbose_name': 'Tagged File',
                'verbose_name_plural': 'Tagged Files',
                'unique_together': {('content_type', 'object_id', 'tag')},
                'index_together': {('content_type', 'object_id')},
            },
        ),
        migrations.CreateModel(
            name='VideoUniqueFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digest', models.CharField(max_length=64, unique=True)),
                ('file_path', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('extension', models.CharField(db_index=True, max_length=10)),
                ('content_type', models.CharField(db_index=True, max_length=255)),
                ('file_size', models.BigIntegerField()),
                ('created_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('modified_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('accessed_time', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DELETED', '已删除'), ('DISABLED', '禁止访问'), ('DRAFT', '草稿'), ('PUBLISHED', '已发布'), ('COLLECTED', '已收藏'), ('ARCHIVED', '已归档')], db_index=True, default='DRAFT', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='webfs.TaggedFile', to='webfs.FileTag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TextUniqueFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digest', models.CharField(max_length=64, unique=True)),
                ('file_path', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('extension', models.CharField(db_index=True, max_length=10)),
                ('content_type', models.CharField(db_index=True, max_length=255)),
                ('file_size', models.BigIntegerField()),
                ('created_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('modified_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('accessed_time', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DELETED', '已删除'), ('DISABLED', '禁止访问'), ('DRAFT', '草稿'), ('PUBLISHED', '已发布'), ('COLLECTED', '已收藏'), ('ARCHIVED', '已归档')], db_index=True, default='DRAFT', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='webfs.TaggedFile', to='webfs.FileTag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PDFUniqueFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digest', models.CharField(max_length=64, unique=True)),
                ('file_path', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('extension', models.CharField(db_index=True, max_length=10)),
                ('content_type', models.CharField(db_index=True, max_length=255)),
                ('file_size', models.BigIntegerField()),
                ('created_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('modified_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('accessed_time', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DELETED', '已删除'), ('DISABLED', '禁止访问'), ('DRAFT', '草稿'), ('PUBLISHED', '已发布'), ('COLLECTED', '已收藏'), ('ARCHIVED', '已归档')], db_index=True, default='DRAFT', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='webfs.TaggedFile', to='webfs.FileTag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ManagedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_path', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('object_digest', models.CharField(db_index=True, max_length=64)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='ImageUniqueFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digest', models.CharField(max_length=64, unique=True)),
                ('file_path', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('extension', models.CharField(db_index=True, max_length=10)),
                ('content_type', models.CharField(db_index=True, max_length=255)),
                ('file_size', models.BigIntegerField()),
                ('created_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('modified_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('accessed_time', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DELETED', '已删除'), ('DISABLED', '禁止访问'), ('DRAFT', '草稿'), ('PUBLISHED', '已发布'), ('COLLECTED', '已收藏'), ('ARCHIVED', '已归档')], db_index=True, default='DRAFT', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='webfs.TaggedFile', to='webfs.FileTag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EBookUniqueFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digest', models.CharField(max_length=64, unique=True)),
                ('file_path', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('extension', models.CharField(db_index=True, max_length=10)),
                ('content_type', models.CharField(db_index=True, max_length=255)),
                ('file_size', models.BigIntegerField()),
                ('created_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('modified_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('accessed_time', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DELETED', '已删除'), ('DISABLED', '禁止访问'), ('DRAFT', '草稿'), ('PUBLISHED', '已发布'), ('COLLECTED', '已收藏'), ('ARCHIVED', '已归档')], db_index=True, default='DRAFT', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='webfs.TaggedFile', to='webfs.FileTag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocUniqueFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digest', models.CharField(max_length=64, unique=True)),
                ('file_path', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('extension', models.CharField(db_index=True, max_length=10)),
                ('content_type', models.CharField(db_index=True, max_length=255)),
                ('file_size', models.BigIntegerField()),
                ('created_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('modified_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('accessed_time', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DELETED', '已删除'), ('DISABLED', '禁止访问'), ('DRAFT', '草稿'), ('PUBLISHED', '已发布'), ('COLLECTED', '已收藏'), ('ARCHIVED', '已归档')], db_index=True, default='DRAFT', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='webfs.TaggedFile', to='webfs.FileTag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AudioUniqueFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digest', models.CharField(max_length=64, unique=True)),
                ('file_path', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('extension', models.CharField(db_index=True, max_length=10)),
                ('content_type', models.CharField(db_index=True, max_length=255)),
                ('file_size', models.BigIntegerField()),
                ('created_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('modified_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('accessed_time', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DELETED', '已删除'), ('DISABLED', '禁止访问'), ('DRAFT', '草稿'), ('PUBLISHED', '已发布'), ('COLLECTED', '已收藏'), ('ARCHIVED', '已归档')], db_index=True, default='DRAFT', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='webfs.TaggedFile', to='webfs.FileTag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
