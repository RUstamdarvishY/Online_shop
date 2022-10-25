from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from mainapp.models import Customer


User = get_user_model()


@receiver(post_save, sender=Customer)
def create_token_for_new_customer(sender, **kwargs):
    if kwargs['created']:
        User.objects.create(user=kwargs['instance'])
