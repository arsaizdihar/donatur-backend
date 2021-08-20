from django.urls import path

from campaign.views import (CampaignList, CampaignListDonorById,
                            CampaignListFundraiser, CampaignListFundraiserById,
                            CampaignListProposal, CampaignListProposalById,
                            DonationView, NotificationCountView,
                            WithdrawRequestView, WithdrawVerifyView)

urlpatterns = [
    path('campaigns/', CampaignList.as_view(), name='campaigns'),
    path('donor/campaigns/<int:pk>/',
         CampaignListDonorById.as_view(), name='campaign-donor-id'),
    path('donate/', DonationView.as_view(), name='donation'),
    path('fundraiser/campaigns/', CampaignListFundraiser.as_view(),
         name='campaign-fundraiser'),
    path('fundraiser/campaigns/<int:pk>/',
         CampaignListFundraiserById.as_view(), name='campaign-fundraiser-id'),
    path('withdraw/', WithdrawRequestView.as_view(), name='withdraw'),
    path('withdraw/requests/', WithdrawVerifyView.as_view(),
         name='withdraw-requests'),
    path('admin/proposals/', CampaignListProposal.as_view(),
         name='campaign-proposal'),
    path('admin/proposals/<int:pk>/', CampaignListProposalById.as_view(),
         name='campaign-proposal-id'),
    path('admin/notification/', NotificationCountView.as_view(),
         name='admin-notification'),
]
