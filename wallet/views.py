from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from users.permissions import IsDonatur

from wallet.models import TopUpHistory

from .serializers import TopUpRequestListSerializer, TopUpRequestSerializer


class TopUpRequestView(generics.CreateAPIView):
    """
    POST    api/topup/  -  Donatur request new top up
    """
    permission_classes = (IsDonatur, )
    serializer_class = TopUpRequestSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            TopUpHistory.objects.create(**serializer.data, user=request.user)
            return Response({"success": True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopUpVerifyView(generics.ListAPIView, generics.UpdateAPIView):
    """
    PUT, PATCH    api/topup/requests/  -  Verify top up request by id
    GET           api/topup/requests/  -  Top up requests list
    """

    permission_classes = (IsAdminUser, )
    queryset = TopUpHistory.objects.filter(verified=False)
    serializer_class = TopUpRequestListSerializer

    def update(self, request, *args, **kwargs):
        id = request.data.get("id")

        if not id:
            return Response({"id": ["This field is required."]}, status.HTTP_400_BAD_REQUEST)
        try:
            int(id)
        except ValueError:
            return Response({"error": ["id must be a number"], "code": "invalid-id"}, status.HTTP_400_BAD_REQUEST)
        top_up_request = get_object_or_404(TopUpHistory, id=id)
        if top_up_request.verified:
            return Response({"error": ["Already verified."], "code": "verified"}, status.HTTP_400_BAD_REQUEST)

        top_up_request.verify()

        return Response({"success": True})
