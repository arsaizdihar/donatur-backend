from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

class TopUpHistory(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE,
                             related_name="top_up_histories", related_query_name="top_up_histories")

    date = models.DateTimeField(auto_now_add=True)

    amount = models.PositiveIntegerField(
        verbose_name="Top Up Amount", default=0)

    status = models.CharField(verbose_name="Top Up Status", max_length=25, choices=(
        ("PENDING", "PENDING"), ("VERIFIED", "VERIFIED"), ("REJECTED", "REJECTED")), default="PENDING")

    bank_name = models.CharField(max_length=255)
    bank_account = models.CharField(max_length=255)
    bank_account_number = models.CharField(
        max_length=255, validators=(RegexValidator(r'^[0-9]+$', "Number only"), ))

    def verify(self):
        if self.status == "PENDING":
            self.status = "VERIFIED"
            self.save()
            user = self.user
            user.wallet_amount += self.amount
            user.save()

    def reject(self):
        if self.status == "PENDING":
            self.status = "REJECTED"
            self.save()

    def __str__(self) -> str:
        return f"{self.user.id} {self.date}"

    class Meta:
        ordering = ("-date", )


class WithdrawRequest(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE,
                             related_name="withdraw_requests", related_query_name="withdraw_requests")
    campaign = models.ForeignKey("campaign.Campaign", on_delete=models.CASCADE,
                                 related_name="withdraw_requests", related_query_name="withdraw_requests")

    request_date = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateTimeField(null=True, blank=True)

    amount = models.PositiveIntegerField(default=0)
    status = models.CharField(verbose_name="Withdraw Status", max_length=25, choices=(
        ("PENDING", "PENDING"), ("VERIFIED", "VERIFIED"), ("REJECTED", "REJECTED")), default="PENDING")

    def verify(self):
        if self.status == "PENDING":
            self.status = "VERIFIED"
            self.verified_date = timezone.now()
            self.save()
            user = self.user
            user.wallet_amount += self.amount
            user.save()
            campaign = self.campaign
            campaign.withdraw_amount -= self.amount
            campaign.save()

    def reject(self):
        if self.status == "PENDING":
            self.status = "REJECTED"
            self.verified_date = timezone.now()
            self.save()

    def __str__(self) -> str:
        return f"{self.campaign.title} {self.amount} {self.request_date}"

    class Meta:
        ordering = ("-request_date", )

class DonationHistory(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE,
                             related_name="donation_histories", related_query_name="donation_histories")

    date = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveIntegerField(default=0)
    campaign = models.ForeignKey("campaign.Campaign", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.campaign.title} {self.amount} {self.date}"

    class Meta:
        ordering = ("-date", )
