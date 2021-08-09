from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import FundraiserRequestSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User(**serializer.data)
        user.set_password(request.data.get("password"))
        user.save()

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
