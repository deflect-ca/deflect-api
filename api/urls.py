from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import edgemanage_view

urlpatterns = [
    path('info', edgemanage_view.api_info, name='api_info'),
    path('edge/list', edgemanage_view.api_edge_query, name='api_edge_query'),
    path('edge/dnet', edgemanage_view.api_dnet_query, name='api_dnet_query'),
    path('edge/config', edgemanage_view.api_edge_conf, name='api_edge_conf'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
