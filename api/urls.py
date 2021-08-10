from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from users.views import FundraiserRequestView, MeView, RegisterView, CampaignProposal, CampaignProposalById

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name="refresh"),
    path('admin/fundraiser-requests/',
         FundraiserRequestView.as_view(), name="fundraiser-requests"),
    path('admin/proposals/', CampaignProposal.as_view(), name='campaign-proposal'),
    path('admin/proposals/<int:pk>/', CampaignProposalById.as_view(), name='campaign-proposal-id'),
    path('me/', MeView.as_view(), name="me"),
    path('', include('campaign.urls')),
    path('', include('wallet.urls'))
]
