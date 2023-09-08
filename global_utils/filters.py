from abc import ABCMeta, abstractmethod
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from taggit.models import Tag


class TagsFilter(SimpleListFilter, metaclass=ABCMeta):
    title = 'Tags'
    parameter_name = 'tags__id__exact'

    @abstractmethod
    def get_model_type(self):
        pass

    def lookups(self, request, model_admin):
        tags = Tag.objects.\
            filter(taggit_taggeditem_items__content_type=ContentType.objects.get_for_model(self.get_model_type())).\
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
