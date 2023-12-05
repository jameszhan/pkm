from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q, Max, Subquery, OuterRef
from .models import FileTag


def date_hierarchy(queryset, year=None, month=None, day=None):
    date_filters = {
        'year': year,
        'month': month,
        'day': day,
    }

    if year and month:
        date_filters['days'] = queryset.filter(created_time__year=year,
                                               created_time__month=month).dates('created_time', 'day')
    elif year:
        date_filters['months'] = queryset.filter(created_time__year=year).dates('created_time', 'month')
    else:
        date_filters['years'] = queryset.dates('created_time', 'year')

    return date_filters


def search_files(model, resource_type=None, status=None, storage_status=None, tag_slugs=None, q=None,
                 year=None, month=None, day=None, sort='-file_size'):
    files = (model.objects.prefetch_related('managed_files').prefetch_related('tags').order_by(sort))
    if resource_type is not None:
        files = files.filter(resource_type=resource_type)
    if status is not None:
        files = files.filter(status=status)
    if storage_status is not None:
        files = files.filter(storage_status=storage_status)

    if tag_slugs:
        tagged_tags = FileTag.objects.filter(slug__in=tag_slugs)
        files = (files.filter(tags__in=tagged_tags).annotate(distinct_tags=Count('tags', distinct=True))
                 .filter(distinct_tags=len(tagged_tags)))
    else:
        tagged_tags = []

    if q:
        files = files.filter(Q(name__icontains=q) | Q(digest__icontains=q))

    if year and month and day:
        files = files.filter(created_time__year=year, created_time__month=month, created_time__day=day)
    elif year and month:
        files = files.filter(created_time__year=year, created_time__month=month)
    elif year:
        files = files.filter(created_time__year=year)
    date_filters = date_hierarchy(files, year, month, day)

    tags = FileTag.objects.filter(
        webfs_taggedfile_items__content_type=ContentType.objects.get_for_model(model),
        webfs_taggedfile_items__object_id__in=files
    ).annotate(file_count=Count('webfs_taggedfile_items')).filter(file_count__gt=0).order_by('-file_count')

    return files, date_filters, tags, tagged_tags
