from api.models import Website
from api.serializers import WebsiteSerializer
from rest_framework import generics


class WebsiteList(generics.ListCreateAPIView):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer


class WebsiteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
