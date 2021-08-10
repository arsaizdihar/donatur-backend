from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import FundraiserProposal, User
from campaign.models import Campaign
from .serializers import (FundraiserRequestSerializer, MeSerializer,
                          RegisterSerializer, CampaignProposalSerializer,
                          CampaignProposalByIdSerializer)


class RegisterView(generics.CreateAPIView):
    """
    POST     api/register/ - Register as DONATUR or FUNDRAISER
    """
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
    """
    ADMIN ONLY
    GET         api/fundraiser-requests/ - List of fundraiser registration requests
    PUT, PATCH  api/fundraiser-requests/ - Verify fundraiser registration by user id
    """

    permission_classes = (permissions.IsAdminUser, )
    serializer_class = FundraiserRequestSerializer
    queryset = User.objects.filter(role="FUNDRAISER", verified=False)

    def update(self, request, *args, **kwargs):
        user_id = request.data.get("id")
        fundraiser_to_verify = get_object_or_404(self.queryset, id=user_id)
        fundraiser_to_verify.verify_fundraiser()
        return Response({"success": True})


class MeView(generics.RetrieveAPIView):
    """
    GET     api/me/  -  Details of current user
    """
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user

class CampaignProposal(generics.ListAPIView):
    """
    GET     api/admin/proposals/ - List of Pending Proposal Campaigns
    """
    queryset = Campaign.objects.filter(status="PENDING")
    serializer_class = CampaignProposalSerializer

class CampaignProposalById(generics.ListAPIView):
    """
    GET     api/admin/proposals/<id>/ - Details of current Pending Proposal Campaign
    """
    queryset = Campaign.objects.all()
    serializer_class = CampaignProposalByIdSerializer
    def get(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
            serializer = self.get_serializer(campaign, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist"}, status=status.HTTP_404_NOT_FOUND)