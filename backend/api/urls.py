from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Health and stats
    path('health', views.health_check, name='health_check'),
    path('stats', views.get_stats, name='get_stats'),

    # Document management
    path('documents/upload', views.upload_document, name='upload_document'),
    path('documents', views.list_documents, name='list_documents'),
    path('documents/delete', views.delete_document, name='delete_document'),

    # RAG query
    path('query', views.query_rag, name='query_rag'),

    # Marketing campaigns
    path('generate-campaign', views.generate_campaign, name='generate_campaign'),
]
