from django.urls import path
from .views import login_page, logout_page, register_page,verify_email

urlpatterns = [
    path('logout/', logout_page, name='logout'),  # Handle logout
    path('login/', login_page, name='login'),  # Handle login using JWT
    path('register/', register_page, name='register'),  # Handle registration
    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
]
