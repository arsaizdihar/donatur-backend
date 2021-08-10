from rest_framework import serializers

from campaign.models import Campaign

class CampaignListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ('title', 'description', 'target_amount', 'created_at', 'status', 'fundraiser', 'image_url')
        read_only_fields = ('created_at', 'status', 'fundraiser')

class CampaignListByIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ('title', 'description', 'target_amount', 'created_at', 'status', 'fundraiser', 'image_url')