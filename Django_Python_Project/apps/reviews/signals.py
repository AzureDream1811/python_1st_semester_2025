from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Review
from .services.sentiment import predict
from apps.products.models import Product
from django.db.models import Avg, Count

@receiver(pre_save, sender=Review)
def compute_sentiment(sender, instance: Review, **kwargs):
    if instance.content:
        label, score = predict(instance.content)
        instance.sentiment = label
        instance.sentiment_score = round(score, 3)

def _recalc_product_rating(product_id: int):
    agg = Review.objects.filter(product_id=product_id, status="approved")\
                        .aggregate(avg=Avg("rating"), cnt=Count("id"))
    Product.objects.filter(id=product_id).update(
        rating_avg=agg["avg"] or 0, rating_count=agg["cnt"] or 0
    )

@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance: Review, created, **kwargs):
    if instance.status == "approved":
        _recalc_product_rating(instance.product_id)

@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance: Review, **kwargs):
    _recalc_product_rating(instance.product_id)
