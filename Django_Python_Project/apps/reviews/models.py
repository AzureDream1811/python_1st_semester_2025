from django.conf import settings
from django.db import models

class Review(models.Model):
    SENTIMENT_CHOICES = [
        ("pos","Positive"),
        ("neg","Negative"),
        ("neu","Neutral"),
        ("unk","Unknown"),
    ]
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="reviews")
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    user = models.CharField(max_length=150, blank=True)
    rating = models.PositiveSmallIntegerField()  # 1..5
    title = models.CharField(max_length=150, blank=True)
    body = models.TextField()
    sentiment_label = models.CharField(max_length=3, choices=SENTIMENT_CHOICES, default="unk")
    sentiment_score = models.FloatField(default=0.0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("product", "user")]  # mỗi người chỉ 1 review 1 sản phẩm

    def __str__(self):
        return f"{self.product} - {self.user} ({self.rating})"
