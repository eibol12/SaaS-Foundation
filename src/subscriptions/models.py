from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db.models.signals import post_save

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
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group) #one-to-one
    permissions = models.ManyToManyField(Permission, limit_choices_to={
        "content_type__app_label": "subscriptions",
        "codename__in": [permission[0] for permission in SUBSCRIPTION_PERMISSIONS]},
        blank=True,
     )


    def __str__(self):
        return self.name

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS

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


