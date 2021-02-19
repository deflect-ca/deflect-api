import logging

from django.http import Http404

from rest_framework import mixins, generics
from rest_framework.response import Response

from api.modules.util import CustomSchema
from api.models import Website, WebsiteOption, Record
from api.serializers import (WebsiteSerializer, WebsiteDetailSerializer,
                             WebsiteOptionSerializer, WebsiteUpdateSerializer,
                             WebsiteCreateSerializer, RecordSerializer,
                             RecordCreateSerializer, RecordModifySerializer)

logger = logging.getLogger(__name__)


class WebsiteList(mixins.ListModelMixin,
                  generics.GenericAPIView):
    """ /api/website/list """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer  # do not show options
    schema = CustomSchema(tags=['website'])

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class WebsiteDetail(mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    """ /api/website/<int:pk> """
    queryset = Website.objects.all()
    serializer_class = WebsiteDetailSerializer  # show options
    schema = CustomSchema(tags=['website'])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class WebsiteCreate(mixins.CreateModelMixin,
                    generics.GenericAPIView):
    """ /api/website/create """
    queryset = Website.objects.all()
    serializer_class = WebsiteCreateSerializer
    schema = CustomSchema(tags=['website'])

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class WebsiteModify(mixins.UpdateModelMixin,
                    generics.GenericAPIView):
    """ /api/website/<int:pk>/modify """
    queryset = Website.objects.all()
    serializer_class = WebsiteUpdateSerializer
    schema = CustomSchema(tags=['website'])

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class WebsiteDelete(mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """ /api/website/<int:pk>/delete """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    schema = CustomSchema(tags=['website'])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class WebsiteListOptions(mixins.ListModelMixin,
                         generics.GenericAPIView):
    """ /api/website/<int:pk>/options """
    serializer_class = WebsiteOptionSerializer
    schema = CustomSchema(tags=['website_options'])

    def get_queryset(self):
        try:
            website = Website.objects.get(
                pk=self.kwargs['pk'])
        except Website.DoesNotExist:
            raise Http404
        return website.options.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class WebsiteOptionsDetail(mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           generics.GenericAPIView):
    """ /api/website/<int:pk>/options/<str:name> """
    serializer_class = WebsiteOptionSerializer
    lookup_field = 'name'
    schema = CustomSchema(tags=['website_options'])

    def get_queryset(self):
        return WebsiteOption.objects.filter(website_id=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class WebsiteListRecords(mixins.ListModelMixin,
                         generics.GenericAPIView):
    """ /api/website/<int:pk>/records """
    serializer_class = RecordSerializer
    schema = CustomSchema(tags=['DNS'])

    def get_queryset(self):
        return Record.objects.filter(website_id=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class WebsiteCreateRecord(mixins.CreateModelMixin,
                          generics.GenericAPIView):
    """ /api/website/<int:pk>/records/create """
    serializer_class = RecordCreateSerializer
    schema = CustomSchema(tags=['DNS'])

    def get_queryset(self):
        return Record.objects.filter(website_id=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        # calls serializer.save()
        return self.create(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        """
        Override default method, insert website_id and call super
        kwargs will be handled in serializer __init__
        """
        kwargs['website_id'] = self.kwargs.get('pk')
        return super(WebsiteCreateRecord, self).get_serializer(*args, **kwargs)

class WebsiteRecordDetail(mixins.RetrieveModelMixin,
                          generics.GenericAPIView):
    """ /api/website/<int:pk>/records/<int:rpk> """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    lookup_url_kwarg = 'rpk'
    schema = CustomSchema(tags=['DNS'])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class WebsiteDeleteRecord(mixins.DestroyModelMixin,
                          generics.GenericAPIView):
    """ /api/website/<int:pk>/records/<int:rpk>/delete """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    lookup_url_kwarg = 'rpk'
    schema = CustomSchema(tags=['DNS'])

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class WebsiteModifyRecord(mixins.UpdateModelMixin,
                          generics.GenericAPIView):
    """ /api/website/<int:pk>/records/<int:rpk>/modify """
    queryset = Record.objects.all()
    serializer_class = RecordModifySerializer
    lookup_url_kwarg = 'rpk'
    schema = CustomSchema(tags=['DNS'])

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
