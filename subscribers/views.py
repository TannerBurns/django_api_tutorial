from rest_framework import viewsets, mixins
from rest_framework.response import Response

from .models import Subscriber
from .serializers import SubscriberSerializer, BulkSubscriberSerializer

class SubscriberView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.DestroyModelMixin):
    serializer_class = SubscriberSerializer

    def get_queryset(self):
        queryset = Subscriber.objects
        if 'state' in self.request.query_params:
            queryset = queryset.filter(location__state__icontains=self.request.query_params['state'])
        return queryset.order_by('created')


    def create(self, request, *args, **kwargs):
        # if the data is a dictionary, use parent create that relies on serializer class
        if isinstance(request.data, dict):
            return super(SubscriberView, self).create(request, *args, **kwargs)
        # if the data is a list, send to the bulk serializer to handle creation
        elif isinstance(request.data, list):
            serializer = BulkSubscriberSerializer(data={'subscribers': request.data})
            if serializer.is_valid():
                serializer.create(request.data)
                return Response(serializer.data, status=201)
            else:
                return Response(serializer.errors, status=400)
        else:
            return Response('Invalid data received', status=400)
