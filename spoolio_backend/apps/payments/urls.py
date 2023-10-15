from django.urls import path

from . import views


urlpatterns = [
    path('create-payment-intent/', views.create_payment),
    path('init-payment-intent/', views.init_payment),
    path('modify-payment-intent/', views.modify_payment),
    path('stripe-webhooks/', views.stripe_webhooks)
]
