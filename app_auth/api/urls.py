from django.urls import path
from .views import RegistrationView, LoginView
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration')
]
