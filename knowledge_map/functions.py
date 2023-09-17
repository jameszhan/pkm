import json
import logging
import traceback
from django.core.cache import cache
from .models import Category, CategoryRelation

logger = logging.getLogger(__name__)


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
    category_dict = {
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
    collector.append(category_dict)

    children = root_category.children.all()
    if len(children) == 0:
        category_dict['type'] = 'leaf'

    for relation in children:
        child_category = relation.child
        if eval_category_relation_context(relation, parent_slug):
            collect_category_tree(child_category, unique_slug, collector)
        if relation.context:
            collector[-1]['context'] = relation.context

    return collector


def get_category_tree(root_category, parent_slug=None):
    unique_slug = f"{parent_slug}/{root_category.slug}" if parent_slug else root_category.slug

    category_dict = {
        'id': root_category.id,
        'name': root_category.name,
        'unique_slug': unique_slug,
        'parent': parent_slug if parent_slug else '#',
        'topic': root_category.topic,
        'children': []
    }

    child_relations = root_category.children_relations.all()

    for relation in child_relations:
        child_category = relation.child
        child_dict = get_category_tree(child_category, unique_slug)

        if relation.context:
            child_dict['context'] = relation.context

        category_dict['children'].append(child_dict)

    return category_dict


def eval_category_relation_context(relation, parent_slug):
    if relation.context:
        try:
            context_config = json.loads(relation.context)
            if 'expression' in context_config:
                expression = context_config['expression']
                ret = eval(expression, {}, {'parent_slug': parent_slug,
                                            'slug': relation.parent.slug,
                                            'child_slug': relation.child.slug})
                # print(f'expression "{expression}" with locals {parent_slug}|{relation.parent.slug}'
                #       f'|{relation.child.slug} and get {ret}')
                if not ret:
                    return False
        except Exception as e:
            logger.error(f"eval expression error: {e}", exc_info=True)
            # traceback.print_exc()
    return True



