from django.contrib import admin
from .models import Category, CategoryRelation


class CategoryRelationInline(admin.TabularInline):
    model = CategoryRelation
    fk_name = 'parent'
    extra = 1


@admin.register(Category)
class CatalogAdmin(admin.ModelAdmin):
    inlines = [CategoryRelationInline]
    list_display = ('id', 'slug', 'name', 'parent_list', 'shorten_topic')
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ['slug', 'name']

    def parent_list(self, obj):
        return ", ".join([str(cat) for cat in obj.parents.all()])
    parent_list.short_description = 'Parents'

    def shorten_topic(self, obj):
        text = obj.topic
        if text is None:
            return None
        return (text[:20] + '...') if len(text) > 20 else text
    shorten_topic.short_description = 'Topic'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('parents')

