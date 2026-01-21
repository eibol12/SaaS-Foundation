from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from helpers import billing
from subscriptions.models import SubscriptionPrice , Subscription, UserSubscription
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()
BASE_URL = settings.BASE_URL

# Create your views here.
def product_price_redirect_view(request, price_id = None, *args, **kwargs):
    request.session["checkout_subscription_price_id"] = price_id
    return redirect("stripe-checkout-start")

@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get("checkout_subscription_price_id")
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj = None
    if checkout_subscription_price_id is None or obj is None:
        return redirect("pricing")
    customer_stripe_id = request.user.customer.stripe_id
    success_url_path = reverse("stripe-checkout-end")
    pricing_url_path = reverse("pricing")
    success_url = f"{BASE_URL}{success_url_path}"
    cancel_url = f"{BASE_URL}{pricing_url_path}"
    price_stripe_id = obj.stripe_id

    url = billing.start_checkout_session(
        customer_id = customer_stripe_id,
        success_url = success_url,
        cancel_url = cancel_url,
        price_stripe_id = price_stripe_id,
        raw = False
    )
    return redirect(url)

@login_required
def checkout_finalize_view(request):
    session_id = request.GET.get("session_id")
    checkout_data = billing.get_checkout_customer_plan(session_id)
    customer_id = checkout_data.pop("customer_id", "")
    plan_id = checkout_data.pop("subscription_plan_price_id", "")
    subscription_stripe_id = checkout_data.pop("subscription_stripe_id", "")
    subscription_data = {**checkout_data}

    try:
        subscription_obj = Subscription.objects.get(subscriptionprice__stripe_id = plan_id)
    except:
        subscription_obj = None
    try:
        user_obj = User.objects.get(customer__stripe_id = customer_id)
    except:
        user_obj = None

    _user_sub_exists = False
    updated_sub_options = {
        "subscription": subscription_obj,
        "stripe_id": subscription_stripe_id,
        "user_cancelled": False,
        **subscription_data
    }
    try:
        _user_sub_obj = UserSubscription.objects.get(user = user_obj)
        _user_sub_exists = True
    except UserSubscription.DoesNotExist:
        _user_sub_obj=UserSubscription.objects.create(
            user = user_obj,
            **updated_sub_options,
        )
    except:
        _user_sub_obj = None
    if None in [subscription_obj, user_obj, _user_sub_obj]:
        return HttpResponseBadRequest("There was an error with your account. Please contact support.")

    if _user_sub_exists:
        #cancel old subscription
        old_stripe_id = _user_sub_obj.stripe_id
        same_stripe_id = subscription_stripe_id == old_stripe_id
        if old_stripe_id is not None and not same_stripe_id:
            try:
                billing.cancel_subscription(
                    stripe_id = old_stripe_id,
                    reason = "Auto ended, new membership started",
                    feedback = "other",
                )
            except:
                pass

        #assign new subscription
        for key , value in updated_sub_options.items():
            setattr(_user_sub_obj, key, value)
        _user_sub_obj.save()
        messages.success(request, "Success! Thank you for joining us.")
        redirect(reverse(_user_sub_obj.get_absolute_url()))
    context = {}
    return render(request, "checkout/success.html", context = context)