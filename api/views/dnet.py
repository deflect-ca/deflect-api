from api.models import Dnet
from api.serializers import DnetSerializer
from api.modules.util import CustomSchema
from rest_framework import generics, mixins


class DnetList(generics.ListCreateAPIView):
    schema = CustomSchema(tags=['dnet'])
    queryset = Dnet.objects.all()
    serializer_class = DnetSerializer


class DnetDetail(mixins.RetrieveModelMixin,
                 mixins.DestroyModelMixin,
                 generics.GenericAPIView):
    """
    We are not using `generics.RetrieveUpdateDestroyAPIView` here
    since dnet shouldn't be allowed to update
    """
    schema = CustomSchema(tags=['dnet'])
    queryset = Dnet.objects.all()
    serializer_class = DnetSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
