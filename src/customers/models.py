from django.db import models
from django.conf import settings
from helpers.billing import create_customer

User = settings.AUTH_USER_MODEL

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True ,blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs): #overriding the default save method
        if not self.stripe_id:
            email = self.user.email
            if email is not None or email != "":
                stripe_id = create_customer(email = email,raw = False)
                self.stripe_id = stripe_id
        super().save(*args, **kwargs)
