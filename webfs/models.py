from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase
from global_utils.functions import human_readable_size


class FileTag(TagBase):
    color = models.CharField(max_length=10, null=True)
    metadata = models.TextField(null=True)

    class Meta:
        verbose_name = "File Tag"
        verbose_name_plural = "File Tags"


class TaggedFile(TaggedItemBase):
    content_object = models.ForeignKey('File', on_delete=models.CASCADE)
    tag = models.ForeignKey(FileTag, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Tagged File"
        verbose_name_plural = "Tagged Files"


class ManagedFile(models.Model):
    original_path = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_digest = models.CharField(max_length=64)
    unique_file = GenericForeignKey('content_type', 'object_digest')


class BaseUniqueFile(models.Model):
    digest = models.CharField(max_length=64, unique=True)
    file_path = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    extension = models.CharField(max_length=10)
    content_type = models.CharField(max_length=255, db_index=True)
    file_size = models.BigIntegerField()
    created_time = models.DateTimeField(null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)
    accessed_time = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    managed_files = GenericRelation(ManagedFile, content_type_field='content_type', object_id_field='object_digest')
    tags = TaggableManager(through=TaggedFile)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name}({human_readable_size(self.file_size)})'


class TextUniqueFile(BaseUniqueFile):
    pass


class ImageUniqueFile(BaseUniqueFile):
    pass


class AudioUniqueFile(BaseUniqueFile):
    pass


class VideoUniqueFile(BaseUniqueFile):
    pass


class PDFUniqueFile(BaseUniqueFile):
    pass


class EBookUniqueFile(BaseUniqueFile):
    pass


class DocUniqueFile(BaseUniqueFile):
    pass

