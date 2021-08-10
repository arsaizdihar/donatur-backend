from django.urls import path

from campaign.views import (
    CampaignList,
    CampaignListFundraiser,
    CampaignListFundraiserById,
    CampaignListProposal,
    CampaignListProposalById
)

urlpatterns = [
    path('campaigns/', CampaignList.as_view(), name='campaigns'),
    path('fundraiser/campaigns/', CampaignListFundraiser.as_view(), name='campaign-fundraiser'),
    path('fundraiser/campaigns/<int:pk>/', CampaignListFundraiserById.as_view(), name='campaign-fundraiser-id'),
    path('admin/proposals/', CampaignListProposal.as_view(), name='campaign-proposal'),
    path('admin/proposals/<int:pk>/', CampaignListProposalById.as_view(), name='campaign-proposal-id'),
]
