from rest_framework import serializers
from wallet.models import DonationHistory, WithdrawRequest

from campaign.models import Campaign

class CampaignListSerializer(serializers.ModelSerializer):
    fundraiser = serializers.SerializerMethodField(
        required=False, read_only=True)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')

    def get_fundraiser(self, obj):
        fundraiser = getattr(obj, "fundraiser", None)
        if not fundraiser:
            return
        return {"full_name": fundraiser.get_full_name(), "email": fundraiser.email}


class DonationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'}, min_length=8, required=True)
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
    fundraiser = serializers.SerializerMethodField(
        required=False, read_only=True)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')
        read_only_fields = ('id', 'created_at', 'amount',
                            'status', 'fundraiser')

    def get_fundraiser(self, obj):
        fundraiser = getattr(obj, "fundraiser", None)
        if not fundraiser:
            return
        return {"full_name": fundraiser.get_full_name(), "email": fundraiser.email}


class CampaignListFundraiserByIdSerializer(serializers.ModelSerializer):
    fundraiser = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url', 'withdraw_amount')

    def get_fundraiser(self, obj):
        fundraiser = getattr(obj, "fundraiser", None)
        if not fundraiser:
            return
        return {"full_name": fundraiser.get_full_name(), "email": fundraiser.email}


class WithdrawSerializer(serializers.ModelSerializer):

    class Meta:
        model = WithdrawRequest
        fields = ('user', 'campaign', 'request_date', 'verified_date', 'amount', 'status')
        read_only_fields = ('user', 'campaign', 'request_date', 'verified_date', 'status')


class WithdrawRequestSerializer(serializers.ModelSerializer):
    campaign = serializers.CharField(
        source='campaign.title', required=False)

    class Meta:
        model = WithdrawRequest
        fields = ('campaign', 'request_date', 'amount', 'status')


class WithdrawVerifySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = WithdrawRequest
        fields = '__all__'


class CampaignListProposalSerializer(serializers.ModelSerializer):
    fundraiser = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')
        read_only_fields = ('id', 'title', 'description', 'target_amount',
                            'created_at', 'fundraiser', 'image_url')

    def get_fundraiser(self, obj):
        fundraiser = getattr(obj, "fundraiser", None)
        if not fundraiser:
            return
        return {"full_name": fundraiser.get_full_name(), "email": fundraiser.email}


class CampaignListProposalByIdSerializer(serializers.ModelSerializer):
    fundraiser = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'description', 'amount', 'target_amount',
                  'created_at', 'status', 'fundraiser', 'image_url')
        read_only_fields = ('id', 'title', 'description', 'amount', 'target_amount',
                            'created_at', 'fundraiser', 'image_url')

    def get_fundraiser(self, obj):
        fundraiser = getattr(obj, "fundraiser", None)
        if not fundraiser:
            return
        return {"full_name": fundraiser.get_full_name(), "email": fundraiser.email}
