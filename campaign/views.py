from rest_framework import generics, permissions, status
from rest_framework.response import Response
from users.permissions import isFundraiser

from .models import Campaign
from .serializers import (
    CampaignListSerializer, 
    CampaignListFundraiserSerializer, 
    CampaignListFundraiserByIdSerializer,
    CampaignListProposalSerializer,
    CampaignListProposalByIdSerializer
)

class CampaignList(generics.ListAPIView):
    """
    Allowed Method: GET
    GET     api/fundraiser/campaigns/ - List Verified Campaigns
    """
    queryset = Campaign.objects.filter(status="VERIFIED")
    serializer_class = CampaignListSerializer

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
        qs = Campaign.objects.filter(fundraiser=request.user.id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        request.data._mutable = True
        data = request.data
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            Campaign.objects.create(**serializer.data, fundraiser=request.user)
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CampaignListFundraiserById(generics.RetrieveDestroyAPIView):
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
            return Response({"status": "campaign doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk, fundraiser=request.user)
            campaign.delete()
        except Campaign.DoesNotExist:
            return Response({"status": "fail"}, status=status.HTTP_404_NOT_FOUND)
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
            return Response({"success": "status updated successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({"status": "campaign doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, pk, *args, **kwargs):
        try:
            campaign = Campaign.objects.get(pk=pk)
            campaign.status = request.data.get("status")
            campaign.save()

            serializer = self.get_serializer(data=campaign, many=False)
            if serializer.is_valid():
                serializer.update()
            return Response({"success": "status updated successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
