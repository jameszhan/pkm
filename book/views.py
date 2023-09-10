import logging
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Publisher, Category, Catalog


JS_TREE_STEP = 1000000
logger = logging.getLogger(__name__)


def healthz(request):
    response = HttpResponse("OK")
    response['X-Client-Host'] = request.get_host()
    return response


def category_tree(request):
    return render(request, 'categories/tree.html', {})


def catalog_tree(request):
    return render(request, 'catalogs/tree.html', {})


def publisher_list(request):
    publishers = Publisher.objects.order_by('isbn')
    paginator = Paginator(publishers, 20)
    page_number = request.GET.get('page', 1)
    publishers = paginator.get_page(page_number)

    return render(request, 'publishers/index.html', locals())


def catalogs_api(request):
    jstree_data = []
    for cat in Catalog.objects.prefetch_related('parents').all():
        # parent_ids = list(cat.parents.values_list('id', flat=True))
        parent_ids = []
        for parent in cat.parents.all():
            parent_ids.append(parent.id)
        if parent_ids:
            for i, parent_id in enumerate(parent_ids):
                cat_id = i * JS_TREE_STEP + cat.id
                jstree_data.append({
                    "id": cat_id,
                    "parent": parent_id,
                    "text": cat.name,
                    "title": cat.topic,
                })
        else:
            jstree_data.append({
                "id": cat.id,
                "parent": '#',
                "text": cat.name,
                "title": cat.topic,
            })

    return JsonResponse(jstree_data, safe=False)


def categories_api(request):
    jstree_data = []
    for category in Category.objects.prefetch_related('parent').all():
        jstree_data.append({
            "id": category.id,
            "parent": category.parent.id if category.parent else "#",
            "text": category.name
        })

    return JsonResponse(jstree_data, safe=False)


def create_category_api(request):
    return HttpResponse(status=204)


def move_category_api(request, cat_id):
    if request.user.is_authenticated:
        target_parent_id = request.POST.get('target_parent_id', None)
        if target_parent_id is None:
            updated_count = 0
        elif target_parent_id == '#':
            updated_count = Category.objects.filter(id=cat_id, created_by=request.user).update(parent_id=None)
        elif target_parent_id.isdigit():
            parent = get_object_or_404(Category, id=int(target_parent_id))
            updated_count = Category.objects.filter(id=cat_id, created_by=request.user).update(parent_id=parent.id)
        else:
            updated_count = 0

        return JsonResponse({'updated_count': updated_count})
    else:
        return JsonResponse({'code': 400, 'message': 'user not authenticated'})


def move_catalog_api(request, cat_id):
    if not request.user.is_authenticated:
        return JsonResponse({'code': 400, 'message': 'user not authenticated'})

    new_parent_id = request.POST.get('new_parent_id')
    if new_parent_id is None or not new_parent_id.isdigit():
        return JsonResponse({'updated_count': 0})

    target = get_object_or_404(Catalog, id=cat_id % JS_TREE_STEP)

    old_parent_id = request.POST.get('old_parent_id')
    old_parent_name = remove_old_parent(old_parent_id, target)

    new_parent = get_object_or_404(Catalog, id=int(new_parent_id) % JS_TREE_STEP)
    target.parents.add(new_parent)

    print("move {} parent from {} to {}".format(target.name, old_parent_name, new_parent.name))
    logger.info("move {} parent from {} to {}", target.name, old_parent_name, new_parent.name)

    return JsonResponse({'updated_count': 1})


def copy_catalog_api(request, cat_id):
    if not request.user.is_authenticated:
        return JsonResponse({'code': 400, 'message': 'user not authenticated'})

    new_parent_id = request.POST.get('new_parent_id')
    if new_parent_id is None or not new_parent_id.isdigit():
        return JsonResponse({'updated_count': 0})

    target = get_object_or_404(Catalog, id=cat_id % JS_TREE_STEP)

    new_parent = get_object_or_404(Catalog, id=int(new_parent_id) % JS_TREE_STEP)
    target.parents.add(new_parent)

    print("copy {} to parent {}".format(target.name, new_parent.name))
    logger.info("copy {} to parent {}", target.name, new_parent.name)

    return JsonResponse({'updated_count': 1})


def delete_catalog_api(request, cat_id):
    if not request.user.is_authenticated:
        return JsonResponse({'code': 400, 'message': 'user not authenticated'})

    target = get_object_or_404(Catalog, id=cat_id % JS_TREE_STEP)

    old_parent_id = request.POST.get('parent_id')
    old_parent_name = remove_old_parent(old_parent_id, target)

    print("delete {} from parent {}".format(target.name, old_parent_name))
    logger.info("delete {} from parent {}", target.name, old_parent_name)

    return JsonResponse({'updated_count': 1})


def remove_old_parent(old_parent_id, target):
    old_parent_name = '#'
    if old_parent_id and old_parent_id.isdigit():
        old_parent = get_object_or_404(Catalog, id=int(old_parent_id) % JS_TREE_STEP)
        old_parent_name = old_parent.name
        target.parents.remove(old_parent)
    return old_parent_name
