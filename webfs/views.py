from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count, Q, Max, Subquery, OuterRef
from django.shortcuts import render
from django.urls import reverse
from .models import Series, FileTag, PDFUniqueFile, VideoUniqueFile, ManagedFile
from .viewhelpers import get_file_server, date_hierarchy, files_by_resource_type


@login_required
def pdf_files(request, series_slug=None):
    files = PDFUniqueFile.objects.prefetch_related('managed_files').prefetch_related('tags').all().order_by('name')

    q = request.GET.get('q', None)
    if q:
        files = files.filter(Q(name__icontains=q) | Q(digest__icontains=q))

    if series_slug is not None:
        files = files.filter(series__slug__iexact=series_slug)

    tag_slugs = request.GET.getlist('tag')
    if tag_slugs:
        tagged_tags = FileTag.objects.filter(slug__in=tag_slugs)
        files = (files.filter(tags__in=tagged_tags).annotate(distinct_tags=Count('tags', distinct=True))
                 .filter(distinct_tags=len(tagged_tags)))
    else:
        tagged_tags = []

    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    if year and month and day:
        files = files.filter(created_time__year=year, created_time__month=month, created_time__day=day)
    elif year and month:
        files = files.filter(created_time__year=year, created_time__month=month)
    elif year:
        files = files.filter(created_time__year=year)

    paginator = Paginator(files, 100)
    page_number = request.GET.get('page', 1)
    files = paginator.get_page(page_number)

    tags = FileTag.objects.filter(
        webfs_taggedfile_items__content_type=ContentType.objects.get_for_model(PDFUniqueFile)
    ).annotate(file_count=Count('webfs_taggedfile_items')).filter(file_count__gt=0).order_by('-file_count')

    series_list = Series.objects.order_by('slug').all()

    return render(request, 'webfs/uniquefiles/index.html', {
        'tagged_tags': tagged_tags,
        'files': files,
        'tags': tags,
        'series_list': series_list,
        'date_filters': date_hierarchy(PDFUniqueFile.objects, year, month, day),
        'file_server': get_file_server(request),
        'index_url': reverse('webfs:pdf_files'),
    })


@login_required
def pdf_files_by_resource_type(request, resource_type):
    return files_by_resource_type(PDFUniqueFile, request, resource_type, 'webfs:pdf_files_by_resource_type')


@login_required
def video_files_by_resource_type(request, resource_type):
    return files_by_resource_type(VideoUniqueFile, request, resource_type, 'webfs:video_files_by_resource_type')


@login_required
def duplicates_pdf_files(request, status=None):
    duplicates = PDFUniqueFile.objects
    if status is not None:
        if status == 'active':
            duplicates = duplicates.exclude(storage_status__in=['ARCHIVED', 'DISABLED', 'DELETED'])
        else:
            duplicates = duplicates.filter(storage_status__iexact=status)

    duplicates = (duplicates.values('name').annotate(name_count=Count('name'), max_file_size=Max('file_size'))
                  .filter(name_count__gt=1).order_by('-name_count', '-max_file_size')
                  .values('name', 'name_count', 'max_file_size'))

    paginator = Paginator(duplicates, 100)
    page_number = request.GET.get('page', 1)
    files = paginator.get_page(page_number)

    return render(request, 'webfs/uniquefiles/duplicates.html', {
        'files': files,
    })


@login_required
def file_list(request):
    files = ManagedFile.objects.order_by('original_path')
    q = request.GET.get('q', None)
    if q:
        files = files.filter(Q(original_path__icontains=q) | Q(object_digest__icontains=q))

    files = files.prefetch_related('unique_file')

    paginator = Paginator(files, 100)
    page_number = request.GET.get('page', 1)
    files = paginator.get_page(page_number)

    return render(request, 'webfs/files/index.html', {
        'files': files,
        'file_server': get_file_server(request),
        'index_url': reverse('webfs:file_list')
    })


def not_use_cdn(request):
    response = JsonResponse({"op": "set_cookie"})
    enabled = request.GET.get('flag', None)
    if enabled:
        response.set_cookie('notUseCDN', '0')
    else:
        response.delete_cookie('notUseCDN')
    return response
