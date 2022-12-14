from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifiers
    for authentication instead of username"""

    def create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # user.set_password(password)
        user.save()
        return user
