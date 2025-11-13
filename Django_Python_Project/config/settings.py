from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    # Django core
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',

    # Third-party
    'crispy_forms', 'widget_tweaks',

    # Local apps
    'apps.accounts',
    'apps.products',
    'apps.cart',
    'apps.orders',
    'apps.reviews.apps.ReviewsConfig',  # quan trọng: để ready() nạp signals & model
    'apps.catalog',  # dùng app này cho trang danh mục/tìm kiếm
]

# User model nếu dùng custom User trong apps/accounts/models.py
AUTH_USER_MODEL = 'accounts.User'  # hoặc bỏ dòng này nếu dùng User mặc định

# Static/Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# MySQL : giữ phần config DB

# FASTTEXT model path
FASTTEXT_MODEL_PATH = str(BASE_DIR / 'ml_models' / 'sentiment_model.bin')

# Cart session key để map với bảng cart_cart
CART_SESSION_ID = 'cart_session_key'

# Template context processors: thêm cart_count
TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.cart.context_processors.cart_counter',  # <-- thêm dòng này
            ],
        },
    },
]
