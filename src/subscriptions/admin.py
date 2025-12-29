from django.contrib import admin

# Register your models here.
from .models import Subscription, UserSubscription, SubscriptionPrice

class SubscriptionPriceInLine(admin.TabularInline):
    model = SubscriptionPrice
    extra = 0
    readonly_fields = ["stripe_id"]
    can_delete = False

class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionPriceInLine]
    list_display = ["name", "active"]
    readonly_fields = ["stripe_id"]


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSubscription)
