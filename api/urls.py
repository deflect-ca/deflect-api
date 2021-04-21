from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import edgemanage, website, integration

urlpatterns = [

    # website
    path('website/list',
        website.WebsiteList.as_view(), name='api_website_list'),
    path('website/create',
        website.WebsiteCreate.as_view(), name='api_website_create'),
    path('website/<int:pk>',
        website.WebsiteDetail.as_view(), name='api_website_detail'),
    path('website/<int:pk>/modify',
        website.WebsiteModify.as_view(), name='api_website_modify'),
    path('website/<int:pk>/delete',
        website.WebsiteDelete.as_view(), name='api_website_delete'),

    # website.options
    path('website/<int:pk>/options',
        website.WebsiteListOptions.as_view(), name='api_website_list_options'),
    path('website/<int:pk>/options/<str:name>',
        website.WebsiteOptionsDetail.as_view(), name='api_website_options_detail'),

    # website.records
    path('website/<int:pk>/records',
        website.WebsiteListRecords.as_view(), name='api_website_list_records'),
    path('website/<int:pk>/records/create',
        website.WebsiteCreateRecord.as_view(), name='api_website_create_record'),
    path('website/<int:pk>/records/<int:rpk>',
        website.WebsiteRecordDetail.as_view(), name='api_website_record_detail'),
    path('website/<int:pk>/records/<int:rpk>/modify',
        website.WebsiteModifyRecord.as_view(), name='api_website_modify_record'),
    path('website/<int:pk>/records/<int:rpk>/delete',
        website.WebsiteDeleteRecord.as_view(), name='api_website_delete_record'),

    # edgemanage
    path('edgemanage/list',
        edgemanage.Edge.as_view(), name='api_edge_list'),
    path('edgemanage/config',
        edgemanage.EdgeConf.as_view(), name='api_edge_config'),
    path('edgemanage/dnet',
        edgemanage.Dnet.as_view(), name='api_dnet_list'),

    # integration
    path('integration/gen_site_config',
        integration.GenSiteConfig.as_view(), name='api_gen_site_config')
]

urlpatterns = format_suffix_patterns(urlpatterns)
