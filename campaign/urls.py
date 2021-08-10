from django.urls import path

from campaign.views import (
    CampaignList,
    CampaignListById
)

urlpatterns = [
    path('fundraiser/campaigns/', CampaignList.as_view(), name='campaign-fundraiser'),
    path('fundraiser/campaigns/<int:pk>/', CampaignListById.as_view(), name='campaign-fundraiser-id')
]
