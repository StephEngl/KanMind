from django.urls import path
from .views import BoardListCreateView, BoardRetrieveUpdateDestroyView

urlpatterns = [
    path('', BoardListCreateView.as_view(), name='board-list-create'),
    path('<int:pk>/', BoardRetrieveUpdateDestroyView.as_view(), name='board-retrieve-update-destroy'),
]
