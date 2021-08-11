from django.db.models import fields
from rest_framework import serializers

from .models import TopUpHistory


class TopUpRequestSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(min_value=5000, required=True)

    class Meta:
        model = TopUpHistory
        fields = "__all__"
        read_only_fields = ('id', 'date', 'status', 'user')


class TopUpRequestListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = TopUpHistory
        fields = "__all__"
