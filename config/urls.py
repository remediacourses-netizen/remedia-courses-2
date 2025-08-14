"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.urls import re_path
from django.views.static import serve  # Добавляем стандартный serve для статики
from . import views
# Импорт хранилища должен быть здесь, если оно используется в URL-паттернах
from .storages import GoogleDriveStorage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
]

if settings.DEBUG:
    # В режиме разработки добавляем обработку медиафайлов
    urlpatterns += [
        # Для медиафайлов из Google Drive
        re_path(r'^media/(?P<path>.*)$', GoogleDriveStorage().url),
        
        # Для статических файлов (если нужно)
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ]