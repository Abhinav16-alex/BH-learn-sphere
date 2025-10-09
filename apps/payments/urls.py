```python
from django.urls import path
from .views import (
    CreatePaymentIntentView, ConfirmPaymentView, StripeWebhookView,
    MyTransactionsView, CreateSubscriptionView, CouponValidateView
)

urlpatterns = [
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('confirm-payment/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('my-transactions/', MyTransactionsView.as_view(), name='my-transactions'),
    path('create-subscription/', CreateSubscriptionView.as_view(), name='create-subscription'),
    path('validate-coupon/', CouponValidateView.as_view(), name='validate-coupon'),
]
```
