from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import teacher_homework_list


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('modules/', views.modules, name='modules'),
    path('library/', views.library_subject_list, name='library_subject_list'),
    path('library/<int:subject_id>/', views.library_by_subject, name='library_by_subject'),
    path('blog/', views.blog, name='blog'),
    path('about_courses/', views.about_courses, name='about_courses'),
    path('submit_homework/<int:lesson_id>/', views.submit_homework, name='submit_homework'),
    path('teacher/homeworks/', teacher_homework_list, name='teacher_homework_list'),
    path('check_homework/<int:submission_id>/', views.check_homework, name='check_homework'),
    path('submit_homework_check/<int:submission_id>/', views.submit_homework_check, name='submit_homework_check'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:subject_id>/modules/', views.module_list, name='module_list'),
    path('modules/<int:module_id>/lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),





]
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.BLOGS_IMAGE_URL, document_root=settings.BLOGS_IMAGE_ROOT)