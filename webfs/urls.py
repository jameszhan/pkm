from django.urls import path
from . import views

app_name = 'webfs'

urlpatterns = [
    # path('files/', views.file_list, name="file_list"),
    path('pdfs/', views.pdf_files, name="pdf_files")
]

