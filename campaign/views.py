from rest_framework.response import Response
from rest_framework import status
from rest_framework import (
    permissions,
    generics
)
from .serializers import (
    CampaignListSerializer,
    CampaignListByIdSerializer
)
from users.permissions import isFundraiser

from .models import Campaign

class CampaignList(generics.ListCreateAPIView):
    """
    Allowed Method: GET, POST
    GET     api/fundraiser/campaigns/ - List Campaign from particular fundraiser
    POST    api/fundraiser/campaigns/ - Create Campaign to particular fundraiser (explicit)
    """
    permission_classes = [
        isFundraiser,
        permissions.IsAuthenticatedOrReadOnly
    ]
    queryset = Campaign.objects.all()
    serializer_class = CampaignListSerializer

    def get(self, request):
        qs = Campaign.objects.filter(fundraiser=request.user.id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        request.data._mutable = True
        request.data['fundraiser'] = request.user
        data = request.data
        serializer = Campaign.objects.create(title=data['title'], 
                                            description=data['description'], target_amount=data['target_amount'], 
                                            image_url=data['image_url'], fundraiser=data['fundraiser'])
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

class CampaignListById(generics.RetrieveDestroyAPIView):
    """
    GET     api/fundraiser/campaigns/<id>/ - Retrieve Campaign by id to withdraw the amount
    DELETE  api/fundraiser/campaigns/<id>/ - Delete Campaign by id
    """
    permission_classes = [
        isFundraiser,
        permissions.IsAuthenticated
    ]
    queryset = Campaign.objects.all()
    serializer_class = CampaignListByIdSerializer

    def get(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
            serializer = self.get_serializer(campaign, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Campaign.DoesNotExist:
            return Response({"status": "campaign doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
            campaign.delete()
        except Campaign.DoesNotExist:
            return Response({"status": "fail"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"status": "success"}, status=status.HTTP_200_OK)