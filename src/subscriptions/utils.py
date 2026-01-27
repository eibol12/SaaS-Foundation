from subscriptions.models import UserSubscription, Subscription, SubscriptionStatus
from customers.models import Customer
from helpers import billing
from django.db.models import Q


def refresh_active_users_subscriptions(user_ids=None,
                                       active_only=True,
                                       days_ago = -1,
                                       days_left = -1,
                                       day_start = -1,
                                       day_end = -1,
                                       verbose=False,):
    qs = UserSubscription.objects.all()
    if active_only:
        qs = qs.by_active_trialing()
    if user_ids is not None:
        qs = qs.by_user_ids(user_ids=user_ids)
    if days_ago > -1:
        qs = qs.by_days_ago(days_ago=days_ago)
    if days_left > -1:
        qs = qs.by_days_left(days_left=days_left)
    if day_start > -1 and day_end > -1:
        qs = qs.by_range(
            days_start=day_start,
            days_end=day_end,
            verbose=verbose
        )

    complete_count = 0
    qs_count = qs.count()
    for user_subscription_object in qs:
        if verbose:
            print(f"Updating user {user_subscription_object.user} {user_subscription_object.subscription} {user_subscription_object.current_period_end}.")
        if user_subscription_object.stripe_id:
            subscription_data = billing.get_subscription(
                stripe_id=user_subscription_object.stripe_id,
                raw=False,
            )
            for key, value in subscription_data.items():
                setattr(user_subscription_object, key, value)
            user_subscription_object.save()
            complete_count += 1
    return complete_count == qs_count

def clear_dangling_subscriptions():
    qs = Customer.objects.filter(stripe_id__isnull=False)
    for customer_obj in qs:
        user = customer_obj.user
        customer_stripe_id = customer_obj.stripe_id
        print(f"Sync {user} - {customer_stripe_id} subs and remove old ones.")
        subscriptions = billing.get_customer_active_subscriptions(
            customer_stripe_id = customer_stripe_id
        )
        for sub in subscriptions:
            existing_user_subscription_qs = UserSubscription.objects.filter(
                stripe_id__iexact=f"{sub.id}".strip()
            )
            if existing_user_subscription_qs.exists():
                continue
            billing.cancel_subscription(
                stripe_id = sub.id,
                reason = "Dangling active subscription",
                feedback = "other",
                cancel_at_period_end = False,
            )


def sync_subs_group_permissions():
    # Your logic for syncing subscriptions should go here

    qs = Subscription.objects.filter(active=True)

    for obj in qs:
        sub_perms = obj.permissions.all()
        for group in obj.groups.all():
            group.permissions.set(sub_perms)

