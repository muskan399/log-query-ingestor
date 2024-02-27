from django.urls import path
from .views import LogFilterView

urlpatterns = [
    path('filter/', LogFilterView.as_view(), name='log-filter'),
]
