from django.db import models


class Campaign(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(verbose_name="Campaign Description")

    amount = models.PositiveIntegerField(
        verbose_name="Amount", default=0)
    target_amount = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=255, choices=(
        ("PENDING", "PENDING"), ("VERIFIED", "VERIFIED"), ("REJECTED", "REJECTED"), ("STOPPED", "STOPPED")), default="PENDING")

    fundraiser = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="campaigns", related_query_name="campaigns")

    image_url = models.URLField(blank=True)

    withdraw_amount = models.PositiveIntegerField(
        verbose_name="Withdrawn Amount", default=0)

    def verify(self):
        if self.status == "PENDING":
            self.status = "VERIFIED"
            self.save()

    def stop(self):
        if self.status == "VERIFIED":
            self.status = "STOPPED"
            self.save()

    def __str__(self):
        return f"{self.title}, {self.created_at}"
