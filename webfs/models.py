from abc import ABCMeta, abstractmethod
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase, GenericTaggedItemBase
from global_utils.functions import human_readable_size
from knowledge_map.models import Category


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


class Series(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    topic = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Level(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64, unique=True)
    rule = models.CharField(max_length=768, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class BaseUniqueFile(models.Model):
    RESOURCE_TYPE_CHOICES = (
        ('BOOKS', '图书'),
        ('PERIODICALS', '期刊'),
        ('MANUALS', '手册'),
        ('EDUCATIONAL_MATERIALS', '教育材料'),
        ('REPORTS', '报告'),
        ('PROMOTIONS', '宣传材料'),
        ('ONLINE_CONTENT', '在线内容'),
        ('SLIDES', '演讲稿'),
        ('SPREADSHEETS', '表格'),
        ('NOTES', '笔记'),
        ('CODE', '代码'),
        ('PHOTOS', '照片'),
        ('IMAGES', '图片'),
        ('AUDIO', '音频'),
        ('AUDIOBOOKS', '有声书'),
        ('MUSIC', '音乐'),
        ('PODCASTS', '播客'),
        ('BROADCASTS', '广播'),
        ('SPEECHES', '演讲'),
        ('SOUNDTRACKS', '原声带'),
        ('VIDEO', '视频'),
        ('MOVIES', '电影'),
        ('DOCUMENTARIES', '记录片'),
        ('TV_SHOWS', '电视剧'),
        ('SHORTS', '短片'),
        ('OTHER', '其他资源')
    )

    PUBLISH_STATUS_CHOICES = (
        ('LISTING', '上架中'),
        ('LISTED', '已上架'),
        ('DELISTED', '已下架'),
        ('DRAFT', '草稿'),
        ('FORTHCOMING', '待出版'),
        ('PUBLISHED', '已出版'),
    )

    STORAGE_STATUS_CHOICES = (
        ('PENDING', '等待处理'),
        ('STORED', '已存储'),
        ('COLLECTED', '已收藏'),
        ('ARCHIVED', '已归档'),
        ('DISABLED', '禁止访问'),
        ('DELETED', '已删除'),
    )

    digest = models.CharField(max_length=64, unique=True)
    file_path = models.CharField(max_length=255, unique=True)
    resource_type = models.CharField(max_length=32, choices=RESOURCE_TYPE_CHOICES, default='OTHER', db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    extension = models.CharField(max_length=10, db_index=True)
    content_type = models.CharField(max_length=255, db_index=True)
    file_size = models.BigIntegerField()
    created_time = models.DateTimeField(null=True, blank=True, db_index=True)
    modified_time = models.DateTimeField(null=True, blank=True, db_index=True)
    accessed_time = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    rating = models.PositiveIntegerField(default=0, db_index=True)
    status = models.CharField(max_length=16, choices=PUBLISH_STATUS_CHOICES, default='LISTING', db_index=True)
    storage_status = models.CharField(max_length=16, choices=STORAGE_STATUS_CHOICES, default='STORED', db_index=True)
    categories = models.ManyToManyField(Category)
    levels = models.ManyToManyField(Level, blank=True)
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_version = models.ForeignKey('self', to_field='digest', blank=True, null=True, on_delete=models.SET_NULL)
    tags = TaggableManager(through=TaggedFile)
    managed_files = GenericRelation(ManagedFile, content_type_field='content_type', object_id_field='object_id')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name}({human_readable_size(self.file_size)})'

    @classmethod
    @abstractmethod
    def get_resource_type_codes(cls):
        pass

    @classmethod
    def get_resource_type_choices(cls):
        allowed_codes = cls.get_resource_type_codes()
        return [(code, label) for code, label in cls.RESOURCE_TYPE_CHOICES if code in allowed_codes]


class TextUniqueFile(BaseUniqueFile):
    @classmethod
    def get_resource_type_codes(cls):
        return ['BOOKS', 'PERIODICALS', 'MANUALS', 'EDUCATIONAL_MATERIALS', 'REPORTS', 'PROMOTIONS', 'ONLINE_CONTENT',
                'SLIDES', 'NOTES', 'CODE', 'OTHER']


class ImageUniqueFile(BaseUniqueFile):
    @classmethod
    def get_resource_type_codes(cls):
        return ['PHOTOS', 'IMAGES', 'OTHER']


class AudioUniqueFile(BaseUniqueFile):
    @classmethod
    def get_resource_type_codes(cls):
        return ['AUDIO', 'AUDIOBOOKS', 'MUSIC', 'PODCASTS', 'BROADCASTS', 'SPEECHES', 'SOUNDTRACKS', 'OTHER']


class VideoUniqueFile(BaseUniqueFile):
    @classmethod
    def get_resource_type_codes(cls):
        return ['VIDEO', 'MOVIES', 'DOCUMENTARIES', 'TV_SHOWS', 'SHORTS', 'OTHER']


class PDFUniqueFile(BaseUniqueFile):
    @classmethod
    def get_resource_type_codes(cls):
        return ['BOOKS', 'PERIODICALS', 'MANUALS', 'EDUCATIONAL_MATERIALS', 'REPORTS', 'PROMOTIONS', 'ONLINE_CONTENT',
                'SLIDES', 'NOTES', 'CODE', 'OTHER']


class EBookUniqueFile(BaseUniqueFile):
    @classmethod
    def get_resource_type_codes(cls):
        return ['BOOKS', 'PERIODICALS', 'MANUALS', 'EDUCATIONAL_MATERIALS', 'REPORTS', 'PROMOTIONS', 'ONLINE_CONTENT',
                'SLIDES', 'NOTES', 'CODE', 'OTHER']


class DocUniqueFile(BaseUniqueFile):
    @classmethod
    def get_resource_type_codes(cls):
        return ['BOOKS', 'PERIODICALS', 'MANUALS', 'EDUCATIONAL_MATERIALS', 'REPORTS', 'PROMOTIONS', 'ONLINE_CONTENT',
                'SPREADSHEETS', 'SLIDES', 'NOTES', 'CODE', 'OTHER']

