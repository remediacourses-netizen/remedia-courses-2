from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_step1
from . import views
from django.contrib.auth.views import LogoutView
from .views import register_step1, subject_selection, teacher_selection
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('register/', register_step1, name='register'),
    path('subject-selection/', subject_selection, name='subject_selection'),  # 👈 добавь это
    path('teacher-selection/', teacher_selection, name='teacher_selection'),  # 👈 и это
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
]
