from rest_framework import serializers

from campaign.models import Campaign


class CampaignListSerializer(serializers.ModelSerializer):
    fundraiser = serializers.CharField(
        source="fundraiser.get_full_name", required=False)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')
        read_only_fields = ('id', 'created_at', 'amount',
                            'status', 'fundraiser')


class CampaignListByIdSerializer(serializers.ModelSerializer):
    fundraiser = serializers.CharField(
        source="fundraiser.get_full_name", required=False)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')
