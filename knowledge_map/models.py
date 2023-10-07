from django.db import models
from taggit.managers import TaggableManager
from global_utils.functions import human_readable_size


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    topic = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}({self.slug})"

    class Meta:
        db_table = 'km_category'


class CategoryRelation(models.Model):
    parent = models.ForeignKey(Category, related_name='children', on_delete=models.CASCADE)
    child = models.ForeignKey(Category, related_name='parents', on_delete=models.CASCADE)
    context = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'km_category_relation'
        unique_together = ('parent', 'child')


class UniqueFile(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    digest = models.CharField(max_length=64, unique=True)
    content_type = models.CharField(max_length=255, db_index=True)
    file_path = models.CharField(max_length=255, unique=True)
    file_size = models.BigIntegerField()
    created_time = models.DateTimeField(null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)
    accessed_time = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager()

    def __str__(self):
        return f'{self.name}({human_readable_size(self.file_size)})'

    class Meta:
        db_table = 'km_unique_file'


class ManagedFile(models.Model):
    original_path = models.CharField(max_length=255, unique=True)
    file_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_file = models.ForeignKey(UniqueFile, to_field='digest', on_delete=models.CASCADE, related_name='managed_files', db_column='unique_file_digest')

    class Meta:
        db_table = 'km_managed_file'


