from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('categories/', views.category_tree, name="category_tree"),
    path('api/categories', views.categories_api, name='api_categories'),
    path('api/categories/create', views.create_category_api, name='api_categories_create'),
    path('api/categories/<int:cat_id>/move', views.move_category_api, name='api_categories_move'),
]


