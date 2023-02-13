from django.urls import path, include

from . import views


urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),

    path('accounts/', include('allauth.urls')),
    
    path('registration/google/', views.GoogleLogin.as_view(), name='google_login'),
]