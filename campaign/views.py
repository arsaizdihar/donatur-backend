from rest_framework import generics, permissions, status
from rest_framework.response import Response
from users.permissions import isFundraiser, IsDonatur

from wallet.models import DonationHistory
from .models import Campaign

from .serializers import (
    CampaignListSerializer, 
    CampaignListFundraiserSerializer, 
    CampaignListFundraiserByIdSerializer,
    CampaignListProposalSerializer,
    CampaignListProposalByIdSerializer,
    DonationSerializer,
    DonationViewSerializer,
)

class CampaignList(generics.ListAPIView):
    """
    Allowed Method: GET
    GET     api/campaigns/ - List Verified Campaigns
    """
    queryset = Campaign.objects.filter(status="VERIFIED")
    serializer_class = CampaignListSerializer

class CampaignListDonorById(generics.RetrieveAPIView, generics.CreateAPIView):
    """
    Allowed Method: GET, POST
    GET     api/donor/campaigns/<int:id>/ - Retrieve Verified Campaign
    POST    api/donor/campaigns/<int:id>/ - Donate a Campaign
    """
    permission_classes = [
        IsDonatur,
        permissions.IsAuthenticated
    ]
    queryset = Campaign.objects.filter(status="VERIFIED")
    serializer_class = CampaignListSerializer

    def get(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
            serializer = self.get_serializer(campaign, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, pk):
        data = request.data
        user = request.user
        campaign = Campaign.objects.get(pk=pk)
        serializer = DonationSerializer(data=data)
        amount = data['amount']

        if not user.check_password(data.get('password')):
            return Response({"status": "Password didn't match."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.wallet_amount >= amount:
            return Response({"status": "Unable to process payment: Your wallet is low."}, status=status.HTTP_400_BAD_REQUEST)

        if not campaign.target_amount >= amount:
            return Response({"status": "Your contribution exceeds target of donation program."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            DonationHistory.objects.create(**serializer.data, user=request.user, campaign=campaign)
            user.wallet_amount -= amount
            user.save()
            campaign.amount += amount
            campaign.save()
            return Response({"status": "Donation successfully transferred to campaign."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DonationView(generics.ListAPIView):
    """
    Allowed Method: GET
    GET     api/donate/ - List of Donation History
    """
    permission_classes = [
        IsDonatur,
        permissions.IsAuthenticated
    ]
    serializer_class = DonationViewSerializer

    def get_queryset(self):
        return DonationHistory.objects.filter(user=self.request.user)

class CampaignListFundraiser(generics.ListCreateAPIView):
    """
    Allowed Method: GET, POST
    GET     api/fundraiser/campaigns/ - List Campaign from particular fundraiser
    POST    api/fundraiser/campaigns/ - Create Campaign to particular fundraiser
    """
    permission_classes = [
        isFundraiser,
        permissions.IsAuthenticated
    ]
    queryset = Campaign.objects.all()
    serializer_class = CampaignListFundraiserSerializer

    def get(self, request):
        campaigns = Campaign.objects.filter(fundraiser=request.user.id)
        serializer = self.get_serializer(campaigns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.verified:
            return Response({"status": "fundraiser not verified."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            Campaign.objects.create(**serializer.data, fundraiser=request.user)
            return Response({"status": "successfully create a new donation program."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CampaignListFundraiserById(generics.RetrieveDestroyAPIView, generics.CreateAPIView):
    """
    Allowed Method: GET, DELETE
    GET     api/fundraiser/campaigns/<id>/ - Retrieve Campaign by id
    DELETE  api/fundraiser/campaigns/<id>/ - Delete Campaign by id
    """
    permission_classes = [
        isFundraiser,
        permissions.IsAuthenticated
    ]
    queryset = Campaign.objects.all()
    serializer_class = CampaignListFundraiserByIdSerializer

    def get(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk, fundraiser=request.user)
            serializer = self.get_serializer(campaign, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk, fundraiser=request.user)
            campaign.delete()
        except Campaign.DoesNotExist:
            return Response({"status": "delete failed. Campaign doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"status": "success"}, status=status.HTTP_200_OK)

class CampaignListProposal(generics.ListAPIView, generics.UpdateAPIView):
    """
    Allowed Method: GET, PUT, PATCH
    GET          api/admin/proposals/ - List of Pending Proposal Campaigns
    PUT, PATCH   api/admin/proposals/ - Verify campaign proposal by campaign id
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = Campaign.objects.filter(status="PENDING")
    serializer_class = CampaignListProposalSerializer

    def update(self, request, *args, **kwargs):
        try:
            campaign_id = request.data.get("id")
            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = request.data.get("status")
            campaign.save()

            serializer = self.get_serializer(data=campaign, many=False)
            if serializer.is_valid():
                serializer.update()
            return Response({"status": "campaign status updated successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

class CampaignListProposalById(generics.RetrieveUpdateAPIView):
    """
    Allowed Method: GET, PUT, PATCH
    GET          api/admin/proposals/<id>/ - Details of current Pending Proposal Campaign
    PUT, PATCH   api/admin/proposals/<id>/ - Verify (status) proposal request by id
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = Campaign.objects.filter(status="PENDING")
    serializer_class = CampaignListProposalByIdSerializer

    def get(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
            serializer = self.get_serializer(campaign, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
    def update(self, request, pk, *args, **kwargs):
        try:
            campaign = Campaign.objects.get(pk=pk)
            campaign.status = request.data.get("status")
            campaign.save()

            serializer = self.get_serializer(data=campaign, many=False)
            if serializer.is_valid():
                serializer.update()
            return Response({"status": "campaign status updated successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
