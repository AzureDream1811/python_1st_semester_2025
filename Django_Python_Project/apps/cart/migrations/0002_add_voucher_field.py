# Generated manual migration to ensure voucher field exists
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
        ('promotions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='voucher',
            field=models.ForeignKey(
                to='promotions.Voucher',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                related_name='carts',
                verbose_name='Voucher'
            ),
        ),
    ]
