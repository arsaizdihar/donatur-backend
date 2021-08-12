from rest_framework import serializers

from campaign.models import Campaign
from wallet.models import DonationHistory

class CampaignListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')

class DonationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, min_length=8, required=True)
    amount = serializers.IntegerField(min_value=5000, required=True)

    class Meta:
        model = DonationHistory
        fields = ('id', 'user', 'date', 'amount', 'password', 'campaign')
        read_only_fields = ('id', 'user', 'date', 'campaign')

class DonationViewSerializer(serializers.ModelSerializer):
    campaign = serializers.CharField(
        source='campaign.title', required=False)
    
    
    class Meta:
        model = DonationHistory
        fields = ('date', 'campaign', 'amount')

class CampaignListFundraiserSerializer(serializers.ModelSerializer):
    fundraiser = serializers.CharField(
        source="fundraiser.get_full_name", required=False)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')
        read_only_fields = ('id', 'created_at', 'amount',
                            'status', 'fundraiser')


class CampaignListFundraiserByIdSerializer(serializers.ModelSerializer):
    fundraiser = serializers.CharField(
        source="fundraiser.get_full_name", required=False)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')

class CampaignListProposalSerializer(serializers.ModelSerializer):
    fundraiser = serializers.CharField(
        source="fundraiser.get_full_name", required=False)
        
    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')
        read_only_fields = ('id', 'title', 'description', 'target_amount',
                  'created_at', 'fundraiser', 'image_url')

class CampaignListProposalByIdSerializer(serializers.ModelSerializer):
    fundraiser = serializers.CharField(
        source="fundraiser.get_full_name", required=False)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')
        read_only_fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'fundraiser', 'image_url')
