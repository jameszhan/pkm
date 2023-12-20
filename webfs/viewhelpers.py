from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from .services import search_files


def get_file_server(request):
    flag = request.COOKIES.get('notUseCDN')
    if flag:
        return settings.FILE_SERVER
    else:
        return settings.CDN_SERVER


def date_hierarchy(queryset, year=None, month=None, day=None):
    date_filters = {
        'year': year,
        'month': month,
        'day': day,
    }

    if year and month:
        date_filters['days'] = queryset.filter(created_time__year=year, created_time__month=month).dates('created_time', 'day')
    elif year:
        date_filters['months'] = queryset.filter(created_time__year=year).dates('created_time', 'month')
    else:
        date_filters['years'] = queryset.dates('created_time', 'year')

    return date_filters


def files_by_resource_type(model, request, resource_type, url_name):
    q = request.GET.get('q', None)
    s = request.GET.get('status', None)
    ss = request.GET.get('storage_status', None)
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    tag_slugs = request.GET.getlist('tag')

    files, date_filters, tags, tagged_tags = search_files(model, resource_type, s, ss, tag_slugs, q, year, month, day)
    paginator = Paginator(files, 100)
    page_number = request.GET.get('page', 1)
    files = paginator.get_page(page_number)

    return render(request, 'webfs/types/index.html', {
        'files': files,
        'date_filters': date_filters,
        'tags': tags,
        'tagged_tags': tagged_tags,
        'resource_type': resource_type,
        'storage_status': ss,
        'resource_types': model.get_resource_type_choices(),
        'storage_statuses': model.STORAGE_STATUS_CHOICES,
        'current_url_name': url_name,
        'file_server': get_file_server(request),
    })
