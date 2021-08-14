from rest_framework import generics, permissions, status
from rest_framework.response import Response
from users.permissions import IsDonatur, isFundraiser
from wallet.models import DonationHistory, WithdrawRequest

from .models import Campaign
from .serializers import (CampaignListFundraiserByIdSerializer,
                          CampaignListFundraiserSerializer,
                          CampaignListProposalByIdSerializer,
                          CampaignListProposalSerializer,
                          CampaignListSerializer, DonationSerializer,
                          DonationViewSerializer, WithdrawSerializer,
                          WithdrawVerifySerializer, WithdrawRequestSerializer
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

        is_valid = serializer.is_valid()
        serializer_data = dict(serializer.data)
        amount = serializer_data.get('amount', 0)
        password = serializer_data.pop("password", "")
        if not user.wallet_amount >= amount:
            return Response({"status": "Unable to process payment: Your wallet is low."}, status=status.HTTP_400_BAD_REQUEST)

        if not campaign.target_amount >= amount:
            return Response({"status": "Your contribution exceeds target of donation program."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"status": "Password didn't match."}, status=status.HTTP_400_BAD_REQUEST)

        if is_valid:
            DonationHistory.objects.create(
                **serializer_data, user=user, campaign=campaign)
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

    def create(self, request):
        if not request.user.verified:
            return Response({"status": "fundraiser not verified."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer_data = dict(serializer.data)
            serializer_data.pop("fundraiser", None)
            Campaign.objects.create(**serializer_data, fundraiser=request.user)
            return Response({"status": "successfully create a new donation program."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CampaignListFundraiserById(generics.RetrieveDestroyAPIView, generics.CreateAPIView):
    """
    Allowed Method: GET, POST, DELETE
    GET     api/fundraiser/campaigns/<int:id>/ - Retrieve Campaign by id
    POST    api/fundraiser/campaigns/<int:id>/ - Create a withdraw
    DELETE  api/fundraiser/campaigns/<int:id>/ - Delete Campaign by id
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

    def create(self, request, pk):
        if not request.user.verified:
            return Response({"status": "fundraiser not verified."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        user = request.user
        campaign = Campaign.objects.get(pk=pk, fundraiser=user)
        serializer = WithdrawSerializer(data=data)
        is_valid = serializer.is_valid()
        serializer_data = dict(serializer.data)
        amount = serializer_data.get('amount', 0)

        if not amount <= campaign.amount:
            return Response({"status": "Your withdrawal exceeds the current campaign amount."}, status=status.HTTP_400_BAD_REQUEST)

        if is_valid:
            WithdrawRequest.objects.create(
                **serializer.data, user=user, campaign=campaign)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response({"status": "failed withdraw"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk, fundraiser=request.user)
            campaign.delete()
            return Response({"status": "campaign successfully deleted"}, status=status.HTTP_200_OK)
        except Campaign.DoesNotExist:
            return Response({"status": "delete failed. Campaign doesn't exist."}, status=status.HTTP_404_NOT_FOUND)


class WithdrawRequestView(generics.ListCreateAPIView):
    """
    Allowed Method: GET
    GET         api/withdraw/ - List of Withdraw Request
    """
    permission_classes = [
        isFundraiser,
        permissions.IsAuthenticated
    ]
    serializer_class = WithdrawRequestSerializer

    def get_queryset(self):
        WithdrawRequest.objects.filter(user=self.request.user)


class WithdrawVerifyView(generics.ListAPIView, generics.UpdateAPIView):
    """
    Allowed Method: GET, PUT, PATCH
    GET          api/withdraw/requests/ - List of Withdraw Request
    PUT, PATCH   api/withdraw/requests/ - Verify Withdraw Request
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = WithdrawRequest.objects.filter(status="PENDING")
    serializer_class = WithdrawVerifySerializer

    def update(self, request, *args, **kwargs):
        data = request.data
        withdraw_id = data.get("id")
        withdraw_status = data.get("status")
        
        if not withdraw_id:
            return Response({"id": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            int(withdraw_id)
        except ValueError:
            return Response({"error": ["id must be a number"], "code": "invalid-id"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not withdraw_status or withdraw_status not in ("VERIFIED", "REJECTED"):
            return Response({"status": ["Invalid status"]}, status=status.HTTP_400_BAD_REQUEST)

        withdraw = WithdrawRequest.objects.get(id=withdraw_id)

        if withdraw.status == "VERIFIED":
            return Response({"error": ["Already verified."], "code": "verified"}, status=status.HTTP_400_BAD_REQUEST)

        if withdraw.status == "REJECTED":
            return Response({"error": ["Already rejected."], "code": "rejected"}, status=status.HTTP_400_BAD_REQUEST)

        if withdraw_status == "VERIFIED":
            withdraw.verify()
        elif withdraw_status == "REJECTED":
            withdraw.reject()
            
        return Response({"status": "successfully verify the withdraw status."}, status=status.HTTP_204_NO_CONTENT)

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
    GET          api/admin/proposals/<int:id>/ - Details of current Pending Proposal Campaign
    PUT, PATCH   api/admin/proposals/<int:id>/ - Verify (status) proposal request by id
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
