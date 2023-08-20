from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Category


def category_tree(request):
    return render(request, 'categories/tree.html', {})


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
