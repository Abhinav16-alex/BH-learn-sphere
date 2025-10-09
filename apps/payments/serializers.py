```python
from rest_framework import serializers
from .models import Transaction, Subscription, Coupon, CouponUsage

class TransactionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user', 'status', 'stripe_payment_intent_id', 'stripe_charge_id', 'created_at', 'completed_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['user', 'stripe_subscription_id', 'stripe_customer_id', 'created_at']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class CouponUsageSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = '__all__'
```
