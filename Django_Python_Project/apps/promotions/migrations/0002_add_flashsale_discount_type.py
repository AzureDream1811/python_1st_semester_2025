from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("promotions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="flashsale",
            name="discount_type",
            field=models.CharField(
                max_length=20,
                choices=[("fixed", "Giá cố định"), ("percentage", "Phần trăm")],
                default="percentage",
                verbose_name="Loại giảm giá",
            ),
        ),
    ]
