from django.urls import path
from .views import ingest_log

urlpatterns = [
    path('', ingest_log, name='ingest_log'),
]
