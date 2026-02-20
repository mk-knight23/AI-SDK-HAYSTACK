from django.urls import path
from . import views

urlpatterns = [
    path('health', views.health_check, name='health_check'),
    path('generate-campaign', views.generate_campaign, name='generate_campaign'),
]
