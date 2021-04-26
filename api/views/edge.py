from api.models import Edge, Dnet
from api.serializers import EdgeSerializer
from api.modules.util import CustomSchema
from rest_framework import generics


class EdgeList(generics.ListCreateAPIView):
    schema = CustomSchema(tags=['edge'])
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer

    def get_queryset(self):
        queryset = Edge.objects.all()
        dnet_name = self.request.query_params.get('dnet')
        dnet_inst = Dnet.objects.filter(name=dnet_name).first()
        if dnet_inst is not None:
            queryset = queryset.filter(dnet=dnet_inst)
        return queryset


class EdgeDetail(generics.RetrieveUpdateDestroyAPIView):
    schema = CustomSchema(tags=['edge'])
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
