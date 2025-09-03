"""
URL configuration for task-related API endpoints.

Exposes RESTful routes for:
- Full CRUD operations on Tasks at the base path.
- Nested routes for Comments on specific tasks.
- Filtering endpoints for tasks assigned to or reviewed by the current user.

Conventions:
- Uses DRF DefaultRouter and NestedDefaultRouter for route handling.
- Named routes support reverse URL resolution.
"""

# 1. Standard library
from django.urls import path, include

# 2. Third-party
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

# 3. Local imports
from .views import TaskViewSet, AssignedTaskListView, ReviewingTaskListView, CommentViewSet


router = DefaultRouter()
router.register(r'', TaskViewSet, basename='task')

comments_router = routers.NestedDefaultRouter(router, r'', lookup='task')
comments_router.register(r'comments', CommentViewSet, basename='task-comments')

urlpatterns = [
    path('assigned-to-me/', AssignedTaskListView.as_view(), name='assigned-tasks'),
    path('reviewing/', ReviewingTaskListView.as_view(), name='reviewing-tasks'),
    path('', include(router.urls)),
    path('', include(comments_router.urls)),
]