"""URL mappings for the user API."""
from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('register/', views.SignupView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path(
        'update-password/',
        views.UpdatePasswordView.as_view(),
        name='update-password'
    ),
    path('search/', views.UserSearchView.as_view(), name='search_user_by_email'),
]
