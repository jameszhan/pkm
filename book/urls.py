from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('publishers/', views.publisher_list, name="publishers"),
    path('categories/', views.category_tree, name="category_tree"),
    path('catalogs/', views.catalog_tree, name="catalog_tree"),
    path('api/categories', views.categories_api, name='api_categories'),
    path('api/categories/create', views.create_category_api, name='api_categories_create'),
    path('api/categories/<int:cat_id>/move', views.move_category_api, name='api_categories_move'),
    path('api/catalogs', views.catalogs_api, name='api_catalogs'),
    path('api/catalogs/<int:cat_id>/move', views.move_catalog_api, name='api_catalogs_move'),
    path('api/categories/<int:cat_id>/copy', views.copy_catalog_api, name='api_catalogs_copy'),
    path('api/categories/<int:cat_id>/delete', views.delete_catalog_api, name='api_catalogs_delete'),
]


