from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase, GenericTaggedItemBase
from global_utils.functions import human_readable_size


class FileTag(TagBase):
    color = models.CharField(max_length=10, null=True)
    metadata = models.TextField(null=True)

    class Meta:
        verbose_name = "File Tag"
        verbose_name_plural = "File Tags"


class TaggedFile(GenericTaggedItemBase):
    tag = models.ForeignKey(
        FileTag, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Tagged File"
        verbose_name_plural = "Tagged Files"
        index_together = [["content_type", "object_id"]]
        unique_together = [["content_type", "object_id", "tag"]]


class ManagedFile(models.Model):
    original_path = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_digest = models.CharField(max_length=64, db_index=True)
    unique_file = GenericForeignKey('content_type', 'object_id')


class BaseUniqueFile(models.Model):
    FILE_STATUS_CHOICES = (
        ('DELETED', '已删除'),
        ('DISABLED', '禁止访问'),
        ('LISTING', '上架中'),
        ('LISTED', '已上架'),
        ('DELISTED', '已下架'),
        ('DRAFT', '草稿'),
        ('FORTHCOMING', '待出版'),
        ('PUBLISHED', '已出版'),
        ('COLLECTED', '已收藏'),
        ('ARCHIVED', '已归档'),
    )

    digest = models.CharField(max_length=64, unique=True)
    file_path = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    extension = models.CharField(max_length=10, db_index=True)
    content_type = models.CharField(max_length=255, db_index=True)
    file_size = models.BigIntegerField()
    created_time = models.DateTimeField(null=True, blank=True, db_index=True)
    modified_time = models.DateTimeField(null=True, blank=True, db_index=True)
    accessed_time = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=FILE_STATUS_CHOICES, default='LISTING', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    managed_files = GenericRelation(ManagedFile, content_type_field='content_type', object_id_field='object_id')
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

