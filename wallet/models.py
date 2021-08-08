from campaign.models import Campaign
from django.db import models
from django.db.models.base import Model


class TopUpHistory(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE,
                             related_name="top_up_histories", related_query_name="top_up_histories")

    date = models.DateTimeField(auto_now_add=True)

    amount = models.PositiveIntegerField(
        verbose_name="Top Up Amount", default=0)

    verified = models.BooleanField(verbose_name="Top Up Verified")
    bank_name = models.CharField(max_length=255)
    bank_account = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.user.id} {self.date}"


class WithdrawRequest(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE,
                             related_name="withdraw_requests", related_query_name="withdraw_requests")
    campaign = models.ForeignKey("campaign.Campaign", on_delete=models.CASCADE,
                                 related_name="withdraw_requests", related_query_name="withdraw_requests")

    request_date = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateTimeField(null=True, blank=True)

    amount = models.PositiveIntegerField(default=0)
    verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.campaign.title} {self.amount} {self.request_date}"


class DonationHistory(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE,
                             related_name="donation_histories", related_query_name="donation_histories")

    date = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveIntegerField(default=0)
    campaign = models.ForeignKey("campaign.Campaign", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.campaign.title} {self.amount} {self.date}"
