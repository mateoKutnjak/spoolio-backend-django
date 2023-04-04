from django.urls import path

from . import views


urlpatterns = [
    path('slicer-estimation/', views.slicer_estimation),
]
