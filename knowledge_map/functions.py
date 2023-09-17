from django.core.cache import cache
from .models import Category, CategoryRelation


def get_all_root_categories():
    root_categories = cache.get('root_categories', [])
    if not root_categories:
        categories_with_parents = CategoryRelation.objects.all().values_list('child', flat=True)
        root_categories = list(Category.objects.exclude(id__in=categories_with_parents))
        cache.set('root_categories', root_categories, 60 * 60)
    return root_categories


def collect_category_tree(root_category, parent_slug=None, collector=None):
    if collector is None:
        collector = []

    unique_slug = f"{parent_slug}/{root_category.slug}" if parent_slug else root_category.slug
    catalog_dict = {
        'id': unique_slug,
        'parent': parent_slug if parent_slug else '#',
        'text': root_category.name,
        'type': 'default' if parent_slug else 'root',
        'a_attr': {
            'title': root_category.topic,
        },
        'data': {
            'id': root_category.id,
            'slug': root_category.slug,
        },
    }
    collector.append(catalog_dict)

    children = root_category.children.all()
    if len(children) == 0:
        catalog_dict['type'] = 'leaf'
    for relation in children:
        child_catalog = relation.child
        collect_category_tree(child_catalog, unique_slug, collector)
        if relation.context:
            collector[-1]['context'] = relation.context

    return collector


def get_category_tree(root_category, parent_slug=None):
    unique_slug = f"{parent_slug}/{root_category.slug}" if parent_slug else root_category.slug

    catalog_dict = {
        'id': root_category.id,
        'name': root_category.name,
        'unique_slug': unique_slug,
        'parent': parent_slug if parent_slug else '#',
        'topic': root_category.topic,
        'children': []
    }

    child_relations = root_category.children_relations.all()

    for relation in child_relations:
        child_catalog = relation.child
        child_dict = get_category_tree(child_catalog, unique_slug)

        if relation.context:
            child_dict['context'] = relation.context

        catalog_dict['children'].append(child_dict)

    return catalog_dict
