from django.urls import path
from .views import RegisterUser, AuthenticateUser

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('authenticate/', AuthenticateUser.as_view(), name='authenticate'),
] 