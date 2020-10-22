from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import edgemanage, website

urlpatterns = [
    # Custom API
    path('info', edgemanage.api_info, name='api_info'),
    path('edge/list', edgemanage.api_edge_query, name='api_edge_query'),
    path('edge/dnet', edgemanage.api_dnet_query, name='api_dnet_query'),
    path('edge/config', edgemanage.api_edge_conf, name='api_edge_conf'),

    # django-rest-framework
    path('website/list', website.WebsiteList.as_view()),
    path('website/create', website.WebsiteCreate.as_view()),
    path('website/<int:pk>', website.WebsiteDetail.as_view()),
    path('website/<int:pk>/options',
        website.WebsiteListOptions.as_view(), name='website-options'),
    path('website/<int:pk>/options/<str:name>',
        website.WebsiteOptionsDetail.as_view(), name='website-options-detail'),
    path('website/<int:pk>/modify', website.WebsiteModify.as_view()),
    path('website/<int:pk>/delete', website.WebsiteDelete.as_view()),
    path('website/<int:pk>/records',
        website.WebsiteListRecords.as_view(), name='website-records'),
    path('website/<int:pk>/records/create',
        website.WebsiteCreateRecord.as_view(), name='website-records-create'),
    path('website/<int:pk>/records/<int:rpk>',
        website.WebsiteRecordDetail.as_view(), name='website-records-detail'),
    path('website/<int:pk>/records/<int:rpk>/delete',
        website.WebsiteDeleteRecord.as_view(), name='website-records-delete')
]

urlpatterns = format_suffix_patterns(urlpatterns)
