from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.cache import cache
from django.db.models import Count
from taggit.forms import TagWidget
from taggit.managers import TaggableManager
from reversion.admin import VersionAdmin
from global_utils.filters import TagsFilter
from .models import Category, Catalog, Publisher, Author, Book


class BookTagsFilter(TagsFilter):
    def get_model_type(self):
        return Book


class CategoriesFilter(SimpleListFilter):
    title = 'categories'
    parameter_name = 'categories'

    def lookups(self, request, model_admin):
        categories = Category.objects.annotate(num_books=Count('books')).filter(num_books__gt=0)
        return [(c.id, c.name) for c in categories.order_by('name')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(categories__id__exact=self.value())
        else:
            return queryset


class PublisherFilter(SimpleListFilter):
    title = 'publisher'
    parameter_name = 'publisher'

    def lookups(self, request, model_admin):
        cached_publishers = cache.get('filtered_publishers')

        if cached_publishers is not None:
            return cached_publishers

        categories = Publisher.objects.only('id', 'name').annotate(num_books=Count('books')).filter(num_books__gt=0)
        result = [(c.id, c.name) for c in categories.order_by('name')]

        cache.set('filtered_publishers', result, 60 * 10) # 10 分钟
        return result

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(publisher__id__exact=self.value())
        else:
            return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('created_by',)
    # readonly_fields = ('created_by',)
    list_display = ('id', 'slug', 'name', 'parent', 'shorten_topic')
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ['slug', 'name']

    def shorten_topic(self, obj):
        text = obj.topic
        if text is None:
            return None
        return (text[:20] + '...') if len(text) > 20 else text
    shorten_topic.short_description = 'Topic'

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
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


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'isbn', 'alias', 'code', 'addr')
    search_fields = ['name', 'isbn', 'alias']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'nationality', 'descriptor', 'aliases')
    search_fields = ['name', 'descriptor']


@admin.register(Book)
class BookAdmin(VersionAdmin):
    list_display = ('id', 'isbn', 'title', 'subtitle', 'author_list', 'category_list', 'publisher', 'rating',
                    'publication_date')
    list_filter = (CategoriesFilter, BookTagsFilter, 'rating', 'publication_date', PublisherFilter)
    search_fields = ['title', 'subtitle', 'isbn']
    date_hierarchy = 'publication_date'
    ordering = ('-publication_date',)

    formfield_overrides = {
        TaggableManager: {'widget': TagWidget(attrs={"size": "80"})}
    }

    def category_list(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    category_list.short_description = 'Categories'

    def author_list(self, obj):
        return ", ".join([str(author) for author in obj.authors.all()])
    author_list.short_description = 'Authors'


