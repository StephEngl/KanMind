from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import TaskViewSet, AssignedTaskListView, ReviewingTaskListView, CommentListView, CommentDeleteView, CommentViewSet

router = DefaultRouter()
router.register(r'', TaskViewSet, basename='task')

comments_router = routers.NestedDefaultRouter(router, r'', lookup='task')
comments_router.register(r'comments', CommentViewSet, basename='task-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(comments_router.urls)),
    path('assigned-to-me', AssignedTaskListView.as_view(), name='assigned-tasks'),
    path('reviewing', ReviewingTaskListView.as_view(), name='reviewing-tasks'),
   ]