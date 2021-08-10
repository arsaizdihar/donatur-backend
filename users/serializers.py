from rest_framework import serializers

from .models import User
from campaign.models import Campaign

class RegisterSerializer(serializers.ModelSerializer):
    proposal_text = serializers.CharField(
        required=False, source="fundraiser_proposal.text")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'password', 'role', 'proposal_text')


class FundraiserRequestSerializer(serializers.ModelSerializer):
    proposal_text = serializers.CharField(source="fundraiser_proposal.text")
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',
                  'email', 'date_joined', 'proposal_text')
        read_only_fields = ('first_name', 'last_name',
                            'email', 'date_joined', 'proposal_text')


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',
                  'role', 'is_staff', 'wallet_amount', 'verified')
        read_only_fields = ('is_staff', 'role', 'wallet_amount', 'verified')
