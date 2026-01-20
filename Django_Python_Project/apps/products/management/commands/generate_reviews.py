"""
Management command để tạo sample reviews cho sản phẩm
Sử dụng comments thực tế từ AIVIVN 2019 dataset (train.csv)
Sử dụng AI FastText để phân tích sentiment thực sự
"""
import os
import random
import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from apps.products.models import Product
from apps.reviews.models import Review
from apps.reviews.sentiment import SentimentAnalyzer


class Command(BaseCommand):
    help = 'Tạo sample reviews từ AIVIVN dataset với AI sentiment analysis'

    # Tên người dùng mẫu cho reviews
    SAMPLE_USERNAMES = [
        'nguyen_van_a', 'tran_thi_b', 'le_van_c', 'pham_thi_d', 'hoang_van_e',
        'vu_thi_f', 'dang_van_g', 'bui_thi_h', 'do_van_i', 'ngo_thi_k',
        'duong_van_l', 'ly_thi_m', 'truong_van_n', 'dinh_thi_o', 'ha_van_p',
        'mai_thi_q', 'vo_van_r', 'tang_thi_s', 'phan_van_t', 'cao_thi_u',
        'lam_van_v', 'to_thi_x', 'trinh_van_y', 'nghiem_thi_z', 'chu_van_aa',
        'khuat_thi_bb', 'quach_van_cc', 'ta_thi_dd', 'mac_van_ee', 'huynh_thi_ff',
        'customer_01', 'customer_02', 'customer_03', 'customer_04', 'customer_05',
        'buyer_01', 'buyer_02', 'buyer_03', 'buyer_04', 'buyer_05',
        'shopper_01', 'shopper_02', 'reviewer_01', 'reviewer_02', 'tech_user_01',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Xoa tat ca reviews cu truoc khi tao moi',
        )
        parser.add_argument(
            '--min-reviews',
            type=int,
            default=5,
            help='So reviews toi thieu cho moi san pham (default: 5)',
        )
        parser.add_argument(
            '--max-reviews',
            type=int,
            default=10,
            help='So reviews toi da cho moi san pham (default: 10)',
        )

    def load_comments_from_csv(self):
        """Load comments từ train.csv"""
        csv_path = os.path.join(settings.BASE_DIR, 'datasets', 'AIVIVN 2019 dataset', 'train.csv')

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.WARNING(f'  [WARNING] Khong tim thay file: {csv_path}'))
            return [], []

        df = pd.read_csv(csv_path)

        # Chia thành positive và negative comments
        positive_comments = df[df['label'] == 1]['comment'].dropna().tolist()
        negative_comments = df[df['label'] == 0]['comment'].dropna().tolist()

        # Lọc comments quá ngắn
        positive_comments = [c.strip() for c in positive_comments if len(str(c).strip()) >= 15]
        negative_comments = [c.strip() for c in negative_comments if len(str(c).strip()) >= 15]

        self.stdout.write(f'  Loaded {len(positive_comments)} positive comments')
        self.stdout.write(f'  Loaded {len(negative_comments)} negative comments')

        return positive_comments, negative_comments

    def handle(self, *args, **options):
        clear_old = options['clear']
        min_reviews = options['min_reviews']
        max_reviews = options['max_reviews']

        if clear_old:
            self.stdout.write(self.style.WARNING('Dang xoa reviews cu...'))
            deleted_count = Review.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'  Da xoa {deleted_count} reviews'))

        self.stdout.write(self.style.WARNING('Bat dau tao reviews...'))

        # Load comments từ CSV
        self.stdout.write('  Dang load comments tu train.csv...')
        positive_comments, negative_comments = self.load_comments_from_csv()

        if not positive_comments and not negative_comments:
            self.stdout.write(self.style.ERROR('  Khong co comments! Dung sample comments mac dinh.'))
            # Fallback comments
            positive_comments = [
                "San pham tuyet voi, chat luong tot!",
                "Rat hai long voi san pham nay.",
                "Giao hang nhanh, dong goi can than.",
                "Dung nhu mo ta, recommend!",
                "Chat luong tuong xung voi gia tien.",
            ]
            negative_comments = [
                "San pham kem, khong nhu mong doi.",
                "That vong ve chat luong.",
                "Giao hang cham, dong goi so sai.",
                "Khong dung nhu mo ta.",
                "Khong dang tien.",
            ]

        # Khởi tạo AI Sentiment Analyzer
        self.stdout.write('  Dang load AI Sentiment model...')
        analyzer = SentimentAnalyzer()
        self.stdout.write(self.style.SUCCESS('  [OK] AI model da san sang'))

        # Tạo users cache
        users_cache = {}
        for username in self.SAMPLE_USERNAMES:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': username.split('_')[0].title(),
                    'last_name': username.split('_')[-1].title() if '_' in username else '',
                    'is_active': True,
                }
            )
            users_cache[username] = user

        products = Product.objects.filter(is_active=True)
        total_reviews = 0

        self.stdout.write(f'  Tao reviews cho {products.count()} san pham...')

        for idx, product in enumerate(products):
            num_reviews = random.randint(min_reviews, max_reviews)
            created_for_product = 0
            attempts = 0
            max_attempts = num_reviews * 3

            while created_for_product < num_reviews and attempts < max_attempts:
                attempts += 1

                # Random rating 1-5
                rating = random.randint(1, 5)

                # Chọn comment phù hợp với rating
                if rating >= 4:
                    comment = random.choice(positive_comments)
                elif rating <= 2:
                    comment = random.choice(negative_comments)
                else:
                    # Neutral - random
                    comment = random.choice(positive_comments + negative_comments)

                # Sử dụng AI để phân tích sentiment
                try:
                    result = analyzer.analyze(comment, rating=rating)
                    sentiment = result['sentiment']
                    sentiment_score = result['score']
                except Exception:
                    # Fallback
                    if rating >= 4:
                        sentiment = 'positive'
                        sentiment_score = 0.5
                    elif rating <= 2:
                        sentiment = 'negative'
                        sentiment_score = -0.5
                    else:
                        sentiment = 'neutral'
                        sentiment_score = 0.0

                # Chọn random user
                username = random.choice(self.SAMPLE_USERNAMES)
                user = users_cache[username]

                # Kiểm tra xem user đã review sản phẩm này chưa
                if Review.objects.filter(product=product, user=user).exists():
                    continue

                # Tạo ngày review ngẫu nhiên trong 6 tháng qua
                days_ago = random.randint(1, 180)
                review_date = timezone.now() - timedelta(days=days_ago)

                # Tạo review
                review = Review.objects.create(
                    product=product,
                    user=user,
                    rating=rating,
                    comment=comment,
                    sentiment=sentiment,
                    sentiment_score=round(sentiment_score, 2),
                    is_approved=True,
                    is_verified_purchase=random.random() < 0.7,
                    helpful_count=random.randint(0, 50),
                )
                review.created_at = review_date
                review.save(update_fields=['created_at'])

                created_for_product += 1
                total_reviews += 1

            # Cập nhật sentiment stats cho product
            product_reviews = Review.objects.filter(product=product, is_approved=True)
            if product_reviews.exists():
                positive_count = product_reviews.filter(sentiment='positive').count()
                negative_count = product_reviews.filter(sentiment='negative').count()
                total_count = product_reviews.count()

                if total_count > 0:
                    product.sentiment_score = round((positive_count - negative_count) / total_count, 2)
                    product.positive_reviews = positive_count
                    product.negative_reviews = negative_count
                    product.save(update_fields=['sentiment_score', 'positive_reviews', 'negative_reviews'])

            # Progress
            if (idx + 1) % 50 == 0:
                self.stdout.write(f'    Da xu ly {idx + 1}/{products.count()} san pham ({total_reviews} reviews)')

        self.stdout.write(self.style.SUCCESS(f'\n[HOAN THANH] Da tao {total_reviews} reviews cho {products.count()} san pham'))
        self.stdout.write(self.style.SUCCESS(f'  Trung binh: {total_reviews / max(products.count(), 1):.1f} reviews/san pham'))
