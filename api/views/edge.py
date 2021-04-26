from api.models import Edge
from api.serializers import EdgeSerializer
from api.modules.util import CustomSchema
from rest_framework import generics


class EdgeList(generics.ListCreateAPIView):
    schema = CustomSchema(tags=['edge'])
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer


class EdgeDetail(generics.RetrieveUpdateDestroyAPIView):
    schema = CustomSchema(tags=['edge'])
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
