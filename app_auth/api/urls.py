"""
URL configuration for authentication-related endpoints.

Exposes RESTful routes for:
- User registration with email and password.
- User login with email and password credential verification.

Conventions:
- Uses class-based views for registration and login.
- Each route includes a name for reverse URL resolution.

Example usage (reverse):
    reverse('registration')
    reverse('login')
"""

# 1. Standard library
from django.urls import path

# 2. Local imports
from .views import RegistrationView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration')
]
