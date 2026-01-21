from django.contrib import admin
from django.urls import path, include
from .views import home_view, about_view, pw_protected_view, user_only_view, staff_only_view
from checkouts import views as checkout_views
from auth import views as auth_views
from subscriptions import views as subscription_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home_view, name="home"),
    path("about/", about_view, name="about"),
    # path("login/", auth_views.login_view, name="login"),
    # path("register/", auth_views.register_view, name="register"),
    path("checkout/sub-price/<int:price_id>/", checkout_views.product_price_redirect_view, name="sub-price-checkout"),
    path("checkout/start/", checkout_views.checkout_redirect_view, name="stripe-checkout-start"),
    path("checkout/success/", checkout_views.checkout_finalize_view, name="stripe-checkout-end"),
    path("pricing/", subscription_views.subscription_price_view, name="pricing"),
    path("accounts/billing/", subscription_views.user_subscription_view, name="user_subscription"),
    path("accounts/billing/cancel", subscription_views.user_subscription_cancel_view, name="user_subscription_cancel"),
    path("accounts/", include("allauth.urls")), #accounts/login/, accounts/register/
    path("protected/", pw_protected_view, name="protected"),
    path("protected/user-only", user_only_view, name="protected_user_only"),
    path("protected/staff-only", staff_only_view, name="protected_staff_only"),
    path("profiles/", include("profiles.urls")),
]
