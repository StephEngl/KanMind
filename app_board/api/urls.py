"""
URL configuration for Board-related API endpoints.

Uses DRF's DefaultRouter to automatically generate routes for BoardViewSet.

Endpoints:
- Base path ('') serves BoardViewSet with standard REST actions (list, retrieve, create, update, delete).
"""

# 1. Standard library
from django.urls import path, include
# 2. Third-party
from rest_framework.routers import DefaultRouter
# 3. Local imports
from .views import BoardViewSet


router = DefaultRouter()
router.register(r'', BoardViewSet, basename='board')

urlpatterns = [
    path('', include(router.urls)),
]
