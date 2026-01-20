from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("promotions", "0002_add_flashsale_discount_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="flashsale",
            name="discount_percent",
            field=models.PositiveIntegerField(default=0, verbose_name='Phần trăm giảm (%)'),
        ),
    ]
