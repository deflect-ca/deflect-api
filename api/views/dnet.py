from api.models import Dnet
from api.serializers import DnetSerializer
from api.modules.util import CustomSchema
from rest_framework import generics


class DnetList(generics.ListCreateAPIView):
    schema = CustomSchema(tags=['dnet'])
    queryset = Dnet.objects.all()
    serializer_class = DnetSerializer


class DnetDetail(generics.RetrieveUpdateDestroyAPIView):
    schema = CustomSchema(tags=['dnet'])
    queryset = Dnet.objects.all()
    serializer_class = DnetSerializer
