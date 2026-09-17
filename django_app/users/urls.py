# django_app/users/urls.py
from django.urls import path
from .views import SignupView, MeView, CustomTokenObtainPairView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
]