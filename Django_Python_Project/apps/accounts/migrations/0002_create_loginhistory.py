from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoginHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("login_time", models.DateTimeField(auto_now_add=True, verbose_name="Thời gian đăng nhập")),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True, verbose_name="Địa chỉ IP")),
                ("device", models.CharField(blank=True, max_length=200, verbose_name="Thiết bị")),
                ("browser", models.CharField(blank=True, max_length=100, verbose_name="Trình duyệt")),
                ("os", models.CharField(blank=True, max_length=100, verbose_name="Hệ điều hành")),
                ("location", models.CharField(blank=True, max_length=200, verbose_name="Vị trí")),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "Thành công"), ("failed", "Thất bại"), ("2fa_required", "Yêu cầu 2FA")],
                        default="success",
                        max_length=20,
                        verbose_name="Trạng thái",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        choices=[("email", "Email/Password"), ("google", "Google"), ("facebook", "Facebook")],
                        default="email",
                        max_length=20,
                        verbose_name="Phương thức",
                    ),
                ),
                ("user_agent", models.TextField(blank=True, verbose_name="User Agent")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="login_history",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Người dùng",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lịch sử đăng nhập",
                "verbose_name_plural": "Lịch sử đăng nhập",
                "ordering": ["-login_time"],
            },
        ),
    ]
