"""
Custom adapters for django-allauth
Để kết nối Google login với User model tùy chỉnh
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for regular account operations
    """

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new User instance using information from the signup form.
        """
        user = super().save_user(request, user, form, commit=False)
        if commit:
            user.save()
        return user

    def get_login_redirect_url(self, request):
        """
        Returns the URL to redirect to after a successful login.
        """
        return '/'


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for Google OAuth operations
    """

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via Google,
        but before the login is actually processed.

        We use this hook to connect the Google account to an existing user
        with the same email.
        """
        if sociallogin.is_existing:
            return

        # Check if email exists
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                existing_user = User.objects.get(email=email)
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up Google user.
        """
        user = super().save_user(request, sociallogin, form)
        data = sociallogin.account.extra_data

        # Update user profile with data from Google
        if hasattr(user, 'profile'):
            profile = user.profile

            # Get name from Google
            if 'name' in data:
                parts = data['name'].split(' ', 1)
                if len(parts) >= 1:
                    user.first_name = parts[0]
                if len(parts) >= 2:
                    user.last_name = parts[1]
                user.save()

            # Get profile picture from Google
            picture_url = data.get('picture')
            if picture_url:
                profile.avatar_url = picture_url
                profile.save()

        return user

    def get_login_redirect_url(self, request):
        """
        Returns the URL to redirect to after a successful Google login.
        """
        return '/'

    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to populate additional user data from Google.
        """
        user = super().populate_user(request, sociallogin, data)

        # Set username from email if not provided
        if not user.username and user.email:
            base_username = user.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username

        return user

