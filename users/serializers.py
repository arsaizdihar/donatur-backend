from rest_framework import serializers

from .models import User


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
