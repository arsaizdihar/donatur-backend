from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import FundraiserProposal, User
from .serializers import (FundraiserRequestSerializer, MeSerializer,
                          RegisterSerializer)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.create_user(**serializer.data)
        except ValueError as e:
            return Response({"proposal_text": [str(e)]}, status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_201_CREATED)


class FundraiserRequestView(generics.ListAPIView, generics.UpdateAPIView):
    permission_classes = (permissions.IsAdminUser, )
    serializer_class = FundraiserRequestSerializer
    queryset = User.objects.filter(role="FUNDRAISER", verified=False)

    def update(self, request, *args, **kwargs):
        user_id = request.data.get("id")
        fundraiser_to_verify = get_object_or_404(self.queryset, id=user_id)
        fundraiser_to_verify.verify_fundraiser()
        return Response({"success": True})


class MeView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user
