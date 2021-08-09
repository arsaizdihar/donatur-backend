from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class User(AbstractUser):
    username = None

    email = models.EmailField('Email address', unique=True)

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
