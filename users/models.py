from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    verified = models.BooleanField(
        verbose_name="Fundraiser Verified", default=False)
    wallet_amount = models.IntegerField(
        verbose_name="Wallet Amount", default=0)
    role = models.CharField(verbose_name="User Role", max_length=10, choices=(
        ("DONATUR", "DONATUR"), ("FUNDRAISER", "FUNDRAISER")), null=True, blank=True)
