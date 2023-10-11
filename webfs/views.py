from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count, Q, Subquery, OuterRef
from django.shortcuts import render
from django.urls import reverse
from .models import PDFUniqueFile, ManagedFile, FileTag


def date_hierarchy(model, year=None, month=None, day=None):
    date_filters = {
        'year': year,
        'month': month,
        'day': day,
    }

    if year and month:
        date_filters['days'] = model.objects.filter(modified_time__year=year, modified_time__month=month).dates('modified_time', 'day')
    elif year:
        date_filters['months'] = model.objects.filter(modified_time__year=year).dates('modified_time', 'month')
    else:
        date_filters['years'] = model.objects.dates('modified_time', 'year')

    return date_filters


@login_required
def pdf_files(request):
    files = (PDFUniqueFile.objects.prefetch_related('managed_files').prefetch_related('tags').all()
             .order_by('-modified_time'))

    q = request.GET.get('q', None)
    if q:
        files = files.filter(Q(name__icontains=q) | Q(digest__icontains=q))

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
        files = files.filter(modified_time__year=year, modified_time__month=month, modified_time__day=day)
    elif year and month:
        files = files.filter(modified_time__year=year, modified_time__month=month)
    elif year:
        files = files.filter(modified_time__year=year)

    paginator = Paginator(files, 50)
    page_number = request.GET.get('page', 1)
    files = paginator.get_page(page_number)

    tags = FileTag.objects.filter(
        webfs_taggedfile_items__content_type=ContentType.objects.get_for_model(PDFUniqueFile)
    ).annotate(file_count=Count('webfs_taggedfile_items')).filter(file_count__gt=0).order_by('-file_count')

    return render(request, 'webfs/uniquefiles/index.html', {
        'tagged_tags': tagged_tags,
        'files': files,
        'tags': tags,
        'date_filters': date_hierarchy(PDFUniqueFile, year, month, day),
        'file_server': settings.FILE_SERVER,
        'index_url': reverse('webfs:pdf_files')
    })


@login_required
def file_list(request):
    files = ManagedFile.objects.order_by('id')
    q = request.GET.get('q', None)
    if q:
        files = files.filter(Q(original_path__icontains=q) | Q(object_digest__icontains=q))

    files = files.prefetch_related('unique_file')

    paginator = Paginator(files, 50)
    page_number = request.GET.get('page', 1)
    files = paginator.get_page(page_number)

    return render(request, 'webfs/files/index.html', {
        'files': files,
        'file_server': settings.FILE_SERVER,
        'index_url': reverse('webfs:file_list')
    })

