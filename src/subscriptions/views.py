from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from subscriptions.models import SubscriptionPrice , UserSubscription
from helpers import billing
from django.contrib import messages
from subscriptions import utils as subs_utils

# Create your views here.

@login_required
def user_subscription_view(request):
    user_subscription_object , created = UserSubscription.objects.get_or_create(user=request.user)
    # subscription_data = user_subscription_object.serialize()
    if request.method == "POST":
        finished = subs_utils.refresh_active_users_subscriptions(
            user_ids = [request.user.id],
            active_only = False
        )
        if finished:
            messages.success(request, "Your plan details have been updated.")
        else:
            messages.error(request, "Your plan details have not been refreshed.")
        return redirect(user_subscription_object.get_absolute_url())

    context = {
        "subscription":user_subscription_object
    }
    return render(request, "subscriptions/user_detail_view.html", context)

@login_required
def user_subscription_cancel_view(request):
    user_subscription_object , created = UserSubscription.objects.get_or_create(user=request.user)
    # subscription_data = user_subscription_object.serialize()
    if request.method == "POST":
        if user_subscription_object.stripe_id and user_subscription_object.is_active_status:
            if user_subscription_object.cancel_at_period_end:
                messages.warning(request, "Your plan is already scheduled to cancel at the end of the billing period.")
            else:
                subscription_data = billing.cancel_subscription(
                    stripe_id=user_subscription_object.stripe_id,
                    reason = "User wanted to end.",
                    feedback = "other",
                    cancel_at_period_end = True,
                    raw=False,
                )

                for key, value in subscription_data.items():
                    setattr(user_subscription_object, key, value)
                user_subscription_object.save()
                messages.success(request, "Your plan has been cancelled.")
        return redirect(user_subscription_object.get_absolute_url())

    context = {
        "subscription":user_subscription_object
    }
    return render(request, "subscriptions/user_cancel_view.html", context)


def subscription_price_view(request):
    qs = SubscriptionPrice.objects.filter(
        featured=True,
    )
    monthly_qs = qs.filter(
        interval=SubscriptionPrice.IntervalChoices.MONTHLY,
    )
    yearly_qs = qs.filter(
        interval=SubscriptionPrice.IntervalChoices.YEARLY,
    )
    return render(request, "subscriptions/pricing.html", {
        "month_qs":monthly_qs,
        "year_qs":yearly_qs

    })