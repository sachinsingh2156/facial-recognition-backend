from django.urls import path
from .views import RegisterUser, AuthenticateUser, DeleteUser

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('authenticate/', AuthenticateUser.as_view(), name='authenticate'),
    path('delete/<str:unique_id>/', DeleteUser.as_view(), name='delete_user'),
]