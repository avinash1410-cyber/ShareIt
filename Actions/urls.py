from django.urls import path
from .views import upload_file,download_file,protected_view,available_files

urlpatterns = [
    path('upload/', upload_file, name='upload'),  # Handle logout
    path('download/<int:file_id>/', download_file, name='download'),  # Handle login using JWT
    path('privacy/', protected_view, name='privacy'),  # Handle registration
    path('files/', available_files, name='files'),  # Handle registration

]