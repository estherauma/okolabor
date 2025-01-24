"""zanex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

from jaguar.views import IndexView, UploadFileView, schema_view

urlpatterns = [
    # API URLS
    path('api/', IndexView.as_view(), name='api-home'),
    path('api/docs/', schema_view.with_ui(
        'redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('', include('theme.urls')),
    path('api/account/', include('account.urls.api')),
    path('api/content/', include('content.urls')),
    path('', include('recruiting.urls.web')),
    path('api/recruiting/', include('recruiting.urls.api')),
    path('api/file-upload/', UploadFileView.as_view(), name='file-upload'),

    url(r'^uploads/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # WEB URLS
    path('account/', include('account.urls.web')),

    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
