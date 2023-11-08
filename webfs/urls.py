from django.urls import path
from . import views

app_name = 'webfs'

urlpatterns = [
    path('files/', views.file_list, name="file_list"),
    path('pdfs/', views.pdf_files, name="pdf_files"),
    path('pdfs/<str:series_slug>', views.pdf_files, name="pdf_files_by_series"),
    path('pdfs/resources/<str:resource_type>', views.pdf_files_by_path_cond, name="pdf_files_by_resource_type"),
    path('pdfs/resources/<str:resource_type>/<str:status>', views.pdf_files_by_path_cond, name="pdf_files_by_path_cond"),
    path('duplicates/pdfs', views.duplicates_pdf_files, name="duplicates_pdf_files"),
    path('duplicates/pdfs/<str:status>', views.duplicates_pdf_files, name="duplicates_pdf_files_by_status"),
]


