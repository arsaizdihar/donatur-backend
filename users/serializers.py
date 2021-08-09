from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'role')


class FundraiserRequestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'date_joined')
        read_only_fields = ('first_name', 'last_name', 'email', 'date_joined')
