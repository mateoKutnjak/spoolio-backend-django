"""spoolio_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('spoolio_backend.apps.authentication.urls')),
    path('api/', include('spoolio_backend.apps.blog.urls')),
    path('api/', include('spoolio_backend.apps.common.urls')),
    path('api/', include('spoolio_backend.apps.faq.urls')),
    path('api/', include('spoolio_backend.apps.filament.urls')),
    path('api/', include('spoolio_backend.apps.modeling_order.urls')),
    path('api/', include('spoolio_backend.apps.payments.urls')),
    path('api/', include('spoolio_backend.apps.print_job.urls')),
    path('api/', include('spoolio_backend.apps.print_order.urls')),
    path('api/', include('spoolio_backend.apps.printer.urls')),
    path('api/', include('spoolio_backend.apps.slicer_estimation.urls')),
    path('api/', include('spoolio_backend.apps.store.urls')),
    path('api/', include('spoolio_backend.apps.store_order.urls')),
    path('api/', include('spoolio_backend.apps.user_profile.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)