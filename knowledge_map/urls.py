from django.urls import path
from . import views

app_name = 'km'

urlpatterns = [
    path('files/<str:file_type>', views.unique_files, name="unique_files"),
    path('categories/', views.category_tree, name="category_tree"),
    path('categories/<str:cat_slug>', views.category_tree, name="category_tree_slug"),
    path('api/categories', views.api_categories, name='api_categories'),
    path('api/categories/<str:cat_slug>', views.api_categories, name='api_categories_slug'),
    path('api/categories/<str:cat_slug>/move', views.api_move_category, name='api_move_category'),
    path('api/categories/<str:cat_slug>/copy', views.api_copy_category, name='api_copy_category'),
    path('api/categories/<str:cat_slug>/delete', views.api_delete_category, name='api_delete_category'),
]


