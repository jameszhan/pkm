import logging
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from .models import Category, CategoryRelation, UniqueFile
from .functions import collect_category_tree, get_all_root_categories

logger = logging.getLogger(__name__)


def category_tree(request, cat_slug=None):
    if cat_slug:
        get_object_or_404(Category, slug=cat_slug)
    return render(request, 'km/categories/tree.html', locals())


def api_categories(request, cat_slug=None):
    jstree_data = []
    if cat_slug:
        root_category = get_object_or_404(Category, slug=cat_slug)
        collect_category_tree(root_category, None, jstree_data)
    else:
        for root_category in get_all_root_categories():
            collect_category_tree(root_category, None, jstree_data)
    return JsonResponse(jstree_data, safe=False)


def api_move_category(request, cat_slug):
    if not request.user.is_authenticated:
        return JsonResponse({'code': 400, 'message': 'user not authenticated'})

    target = get_object_or_404(Category, slug=cat_slug)
    new_parent_slug = request.POST.get('new_parent_slug')
    if new_parent_slug is None or new_parent_slug == '#':
        return JsonResponse({'updated_count': 0})
    new_parent = get_object_or_404(Category, slug=new_parent_slug.split('/')[-1])

    old_parent_slug = request.POST.get('old_parent_slug')
    old_parent = None
    if old_parent_slug is not None and old_parent_slug != '#':
        old_parent_slug = old_parent_slug.split('/')[-1]
        old_parent = get_object_or_404(Category, slug=old_parent_slug)

    print("move {} from {} to {}".format(target.name,
                                         old_parent.name if old_parent else old_parent_slug,
                                         new_parent.name))
    with transaction.atomic():
        updated_count = 0
        if old_parent:
            deleted_count, _ = CategoryRelation.objects.filter(parent=old_parent, child=target).delete()
            updated_count += deleted_count

        ret = target.parents.create(parent=new_parent)
        if ret:
            updated_count += 1
    return JsonResponse({'updated_count': updated_count})


def api_copy_category(request, cat_slug):
    if not request.user.is_authenticated:
        return JsonResponse({'code': 400, 'message': 'user not authenticated'})

    target = get_object_or_404(Category, slug=cat_slug)
    new_parent_slug = request.POST.get('new_parent_slug')
    if new_parent_slug is None or new_parent_slug == '#':
        return JsonResponse({'updated_count': 0})
    new_parent = get_object_or_404(Category, slug=new_parent_slug.split('/')[-1])

    old_parent_slug = request.POST.get('old_parent_slug')
    old_parent = None
    if old_parent_slug is not None and old_parent_slug != '#':
        old_parent_slug = old_parent_slug.split('/')[-1]
        old_parent = get_object_or_404(Category, slug=old_parent_slug)

    print("copy {} from {} to {}".format(target.name,
                                         old_parent.name if old_parent else old_parent_slug,
                                         new_parent.name))

    updated_count = 0
    ret = target.parents.create(parent=new_parent)
    if ret:
        updated_count += 1

    return JsonResponse({'updated_count': updated_count})


def api_delete_category(request, cat_slug):
    if not request.user.is_authenticated:
        return JsonResponse({'code': 400, 'message': 'user not authenticated'})

    target = get_object_or_404(Category, slug=cat_slug)

    old_parent_slug = request.POST.get('parent_slug')
    old_parent = None
    if old_parent_slug is not None and old_parent_slug != '#':
        old_parent_slug = old_parent_slug.split('/')[-1]
        old_parent = get_object_or_404(Category, slug=old_parent_slug)

    updated_count = 0
    if old_parent:
        deleted_count, _ = CategoryRelation.objects.filter(parent=old_parent, child=target).delete()
        updated_count += deleted_count

    print("delete {} from parent {}".format(target.name, old_parent.name if old_parent else old_parent_slug))
    return JsonResponse({'updated_count': updated_count})


ContentTypes = {
    'pdf': 'application/pdf'
}


def unique_files(request, file_type):
    if file_type not in ContentTypes:
        raise Http404

    files = UniqueFile.objects.filter(content_type__iexact=ContentTypes[file_type])
    paginator = Paginator(files, 20)
    page_number = request.GET.get('page', 1)
    files = paginator.get_page(page_number)

    return render(request, 'km/files/pdf_files.html', {
        "files": files
    })
