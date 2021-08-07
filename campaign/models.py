from django.db import models


class Campaign(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(verbose_name="Campaign Description")
    target_amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=(
        ("PENDING", "PENDING"), ("VERIFIED", "VERIFIED"), ("REJECTED", "REJECTED")), default="PENDING")
    fundraiser = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="campaigns", related_query_name="campaigns")

    def __str__(self):
        return f"{self.title}, {self.created_at}"
