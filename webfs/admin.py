from abc import ABCMeta, abstractmethod
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from taggit.forms import TagWidget
from taggit.managers import TaggableManager
from global_utils.functions import human_readable_size
from .models import (FileTag, TaggedFile, ManagedFile, Series, Level, PDFUniqueFile, TextUniqueFile, ImageUniqueFile,
                     AudioUniqueFile, VideoUniqueFile, EBookUniqueFile, DocUniqueFile)


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
                    'series', 'status')
    list_filter = ['modified_time']
    search_fields = ['name', 'digest']
    date_hierarchy = 'modified_time'
    raw_id_fields = ('current_version',)

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


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ['name', 'slug']


@admin.register(Level)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'rule')
    search_fields = ['code', 'name']


def create_tags_filter(file_type, unique_file_model):
    tags_filter_class_name = f"{file_type}TagsFilter"
    return type(tags_filter_class_name, (TagsFilter,), {
        'get_model_type': lambda self: unique_file_model
    })


def create_admin_class(file_type, tags_filter, additional_filters):
    admin_class_name = f"{file_type}UniqueFileAdmin"
    return type(admin_class_name,  (BaseUniqueFileAdmin,), {
        'list_filter': [tags_filter] + additional_filters
    })


FILE_TYPES = {
    'PDF': (PDFUniqueFile, ['series', 'status', 'resource_type', 'categories', 'modified_time']),
    'Audio': (AudioUniqueFile, ['series', 'content_type', 'status', 'resource_type', 'categories', 'modified_time']),
    'Video': (VideoUniqueFile, ['series', 'content_type', 'status', 'resource_type', 'categories', 'modified_time']),
    'Image': (ImageUniqueFile, ['series', 'content_type', 'status', 'resource_type', 'categories', 'modified_time']),
    'EBook': (EBookUniqueFile, ['series', 'content_type', 'status', 'resource_type', 'categories', 'modified_time']),
    'Doc': (DocUniqueFile, ['series', 'content_type', 'status', 'resource_type', 'categories', 'modified_time']),
    'Text': (TextUniqueFile, ['series', 'content_type', 'status', 'resource_type', 'categories', 'modified_time']),
}


for filetype, (uniquefilemodel, additionalfilters) in FILE_TYPES.items():
    tagsfilter = create_tags_filter(filetype, uniquefilemodel)
    adminclass = create_admin_class(filetype, tagsfilter, additionalfilters)
    admin.site.register(uniquefilemodel, adminclass)






