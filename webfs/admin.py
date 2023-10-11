from abc import ABCMeta, abstractmethod
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from taggit.forms import TagWidget
from taggit.managers import TaggableManager
from global_utils.functions import human_readable_size
from .models import (FileTag, TaggedFile, ManagedFile, PDFUniqueFile, TextUniqueFile, ImageUniqueFile, AudioUniqueFile,
                     VideoUniqueFile, EBookUniqueFile, DocUniqueFile)


class TaggedFileInline(admin.StackedInline):
    model = TaggedFile


@admin.register(FileTag)
class FileTagAdmin(admin.ModelAdmin):
    inlines = [TaggedFileInline]
    list_display = ["id", "name", "slug", "item_count"]
    ordering = ["name", "slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}

    def item_count(self, obj):
        return obj.webfs_taggedfile_items.count()
    item_count.short_description = 'Item Count'


class TagsFilter(SimpleListFilter, metaclass=ABCMeta):
    title = 'Tags'
    parameter_name = 'tags__id__exact'

    @abstractmethod
    def get_model_type(self):
        pass

    def lookups(self, request, model_admin):
        tags = FileTag.objects.\
            filter(webfs_taggedfile_items__content_type=ContentType.objects.get_for_model(self.get_model_type())).\
            distinct()
        filters = []
        for tag in tags:
            filters.append((tag.id, tag.name))
        return filters

    def queryset(self, request, queryset):
        filter_value = self.value()
        if filter_value:
            return queryset.filter(tags__id__exact=self.value())
        return queryset


class BaseUniqueFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_link', 'extension', 'tag_list', 'human_file_size', 'created_time', 'modified_time',
                    'accessed_time', 'status')
    list_filter = ['modified_time']
    search_fields = ['name', 'digest']
    date_hierarchy = 'modified_time'

    def get_tag_filter(self):
        pass

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'tags'

    def name_with_link(self, obj):
        return mark_safe(f'<a href="{settings.FILE_SERVER}/{obj.file_path}" target="_blank">{obj.name}</a>')
    name_with_link.short_description = "Name"
    name_with_link.admin_order_field = "name"

    def human_file_size(self, obj):
        return human_readable_size(obj.file_size)
    human_file_size.short_description = "File Size"
    human_file_size.admin_order_field = "file_size"

    formfield_overrides = {
        TaggableManager: {'widget': TagWidget(attrs={"size": "80"})}
    }


@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'path_with_link', 'unique_file')
    search_fields = ['original_path']

    def path_with_link(self, obj):
        return mark_safe(f'<a href="{settings.FILE_SERVER}/{obj.unique_file.file_path}" target="_blank">{obj.original_path}</a>')
    path_with_link.short_description = "Original Path"
    path_with_link.admin_order_field = "original_path"


class PDFTagsFilter(TagsFilter):
    def get_model_type(self):
        return PDFUniqueFile


@admin.register(PDFUniqueFile)
class PDFUniqueFileAdmin(BaseUniqueFileAdmin):
    list_filter = [PDFTagsFilter, 'modified_time', 'status']


class TextTagsFilter(TagsFilter):
    def get_model_type(self):
        return TextUniqueFile


@admin.register(TextUniqueFile)
class TextUniqueFileAdmin(BaseUniqueFileAdmin):
    list_filter = [PDFTagsFilter, 'modified_time', 'status']


class AudioTagsFilter(TagsFilter):
    def get_model_type(self):
        return AudioUniqueFile


@admin.register(AudioUniqueFile)
class AudioUniqueFileAdmin(BaseUniqueFileAdmin):
    list_filter = [PDFTagsFilter, 'modified_time', 'status']


class VideoTagsFilter(TagsFilter):
    def get_model_type(self):
        return VideoUniqueFile


@admin.register(VideoUniqueFile)
class VideoUniqueFileAdmin(BaseUniqueFileAdmin):
    list_filter = [PDFTagsFilter, 'modified_time', 'status']


class ImageTagsFilter(TagsFilter):
    def get_model_type(self):
        return ImageUniqueFile


@admin.register(ImageUniqueFile)
class ImageUniqueFileAdmin(BaseUniqueFileAdmin):
    list_filter = [PDFTagsFilter, 'modified_time', 'status']


class EBookTagsFilter(TagsFilter):
    def get_model_type(self):
        return EBookUniqueFile


@admin.register(EBookUniqueFile)
class EBookUniqueFileAdmin(BaseUniqueFileAdmin):
    list_filter = [PDFTagsFilter, 'modified_time', 'status']


class DocTagsFilter(TagsFilter):
    def get_model_type(self):
        return DocUniqueFile


@admin.register(DocUniqueFile)
class DocUniqueFileAdmin(BaseUniqueFileAdmin):
    list_filter = [PDFTagsFilter, 'modified_time', 'status']
