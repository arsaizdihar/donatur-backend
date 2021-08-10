from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class User(AbstractUser):
    username = None

    email = models.EmailField('Email address', unique=True)
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)
    verified = models.BooleanField(
        verbose_name="Fundraiser Verified", default=False)
    wallet_amount = models.PositiveIntegerField(
        verbose_name="Wallet Amount", default=0)
    role = models.CharField(verbose_name="User Role", max_length=10, choices=(
        ("DONATUR", "DONATUR"), ("FUNDRAISER", "FUNDRAISER")), null=True, blank=True)
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def verify_fundraiser(self):
        if self.role == "FUNDRAISER":
            self.verified = True
            self.save()


class FundraiserProposal(models.Model):
    fundraiser = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="fundraiser_proposal", related_query_name="fundraiser_proposal", null=True)
    text = models.TextField(null=True, blank=True)
