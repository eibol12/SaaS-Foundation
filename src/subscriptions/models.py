from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db.models.signals import post_save

from helpers.billing import create_product, create_price

User = settings.AUTH_USER_MODEL #auth.User

ALLOW_CUSTOM_GROUPS = True

SUBSCRIPTION_PERMISSIONS = [
            ("advanced", "Advanced Perm"), #access subscriptions.advanced
            ("pro", "Pro Perm"), #access subscriptions.pro
            ("basic", "Basic Perm"), #access subscriptions.basic
            ("basic_ai", "Basic AI Perm"), #access subscriptions.basic
        ]

# Create your models here.
class Subscription(models.Model):
    """
    Subscription Plan = Stripe Product object
    """
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group) #one-to-one
    permissions = models.ManyToManyField(Permission, limit_choices_to={
        "content_type__app_label": "subscriptions",
        "codename__in": [permission[0] for permission in SUBSCRIPTION_PERMISSIONS]},
        blank=True,
     )
    stripe_id = models.CharField(max_length=120, null=True ,blank=True)
    order = models.IntegerField(default=-1, help_text="Order of subscription prices")
    featured = models.BooleanField(default=True, help_text="Featured subscription will be displayed on the home page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
        ordering = ["order", "featured", "-updated"]

    def save(self, *args, **kwargs): #overriding the default save method
        if not self.stripe_id:
            stripe_id = create_product(name = self.name, metadata = {"subscription_plan_id":self.stripe_id},raw = False)
            self.stripe_id = stripe_id

        super().save(*args, **kwargs)

class SubscriptionPrice(models.Model):
    """
    Subscription Price = Stripe Price object
    """
    class IntervalChoices(models.TextChoices):
        MONTHLY = "month", "Monthly"
        YEARLY = "year", "Yearly"

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, blank=True, null=True)
    stripe_id = models.CharField(max_length=120, null=True ,blank=True)
    interval = models.CharField(max_length=120, default=IntervalChoices.MONTHLY, choices=IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1, help_text="Order of subscription prices")
    featured = models.BooleanField(default=True, help_text="Featured subscription will be displayed on the home page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["subscription__order","order", "featured", "-updated"]

    @property
    def stripe_currency(self):
        return "usd"

    @property
    def stripe_price(self):
        """
        Remove decimal places
        :return:
        """
        return int(self.price * 100)

    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id

    def save(self, *args, **kwargs):
        if (not self.stripe_id and
                self.product_stripe_id is not None):
            stripe_id = create_price(
                currency = self.stripe_currency,
                unit_amount = self.stripe_price,
                interval = self.interval,
                product = self.product_stripe_id,
                metadata = {"subscription_plan_price_id":self.stripe_id},
                raw = False,
            )
            self.stripe_id = stripe_id

        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(
                subscription = self.subscription,
                interval = self.interval,
            ).exclude(id=self.id)
            qs.update(featured=False)


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)

def user_subscription_post_save(sender, instance, *args, **kwargs):
    user_subscription_instance = instance
    user = instance.user
    subscription_obj = user_subscription_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list('id', flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups)
    else:
        subscription_qs =Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            subscription_qs = subscription_qs.exclude(id=subscription_obj.id)
        subscription_groups = subscription_qs.values_list("groups__id", flat=True)
        subscription_groups_set = set(subscription_groups)


        current_groups = user.groups.all().values_list('id', flat=True)
        groups_id_set = set(groups_ids)
        current_groups_set = set(current_groups) - subscription_groups_set
        final_group_ids = list(groups_id_set | current_groups_set)
        user.groups.set(final_group_ids)



post_save.connect(user_subscription_post_save, sender=UserSubscription)


