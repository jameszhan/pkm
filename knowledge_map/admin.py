from django.contrib import admin
from global_utils.functions import human_readable_size
from django.utils.safestring import mark_safe
from .models import Category, CategoryRelation, UniqueFile, ManagedFile


class CategoryRelationInline(admin.TabularInline):
    model = CategoryRelation
    fk_name = 'child'
    extra = 1


@admin.register(Category)
class CatalogAdmin(admin.ModelAdmin):
    inlines = [CategoryRelationInline]
    list_display = ('id', 'slug', 'name', 'parent_list', 'shorten_topic')
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ['slug', 'name']

    def parent_list(self, obj):
        return ", ".join([r.parent.name for r in obj.parents.all()])
    parent_list.short_description = 'Parents'

    def shorten_topic(self, obj):
        text = obj.topic
        if text is None:
            return None
        return (text[:20] + '...') if len(text) > 20 else text
    shorten_topic.short_description = 'Topic'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('parents')


@admin.register(UniqueFile)
class UniqueFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_with_link', 'content_type', 'human_file_size', 'created_time', 'modified_time', 'accessed_time')
    search_fields = ['name', 'digest']

    # cd /opt/rootfs/pkm && python3 -m http.server 8888
    def name_with_link(self, obj):
        return mark_safe(f'<a href="http://localhost:8888/{obj.file_path}" target="_blank">{obj.name}</a>')
    name_with_link.short_description = "Name"
    name_with_link.admin_order_field = "name"

    def human_file_size(self, obj):
        return human_readable_size(obj.file_size)
    human_file_size.short_description = "File Size"
    human_file_size.admin_order_field = "file_size"


@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'path_with_link', 'unique_file')
    search_fields = ['original_path']

    def path_with_link(self, obj):
        return mark_safe(f'<a href="http://localhost:8888/{obj.unique_file.file_path}" target="_blank">{obj.original_path}</a>')
    path_with_link.short_description = "Original Path"
    path_with_link.admin_order_field = "original_path"


