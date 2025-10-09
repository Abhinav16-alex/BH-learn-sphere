```python
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
import stripe

from .models import Transaction, Subscription, Coupon
from .serializers import TransactionSerializer, SubscriptionSerializer, CouponSerializer
from apps.courses.models import Course, Enrollment

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        course_id = request.data.get('course_id')
        coupon_code = request.data.get('coupon_code')
        
        course = get_object_or_404(Course, id=course_id)
        
        if course.is_free:
            return Response({'error': 'This course is free'}, status=status.HTTP_400_BAD_REQUEST)
        
        amount = float(course.price)
        
        # Apply coupon if provided
        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_until__gte=timezone.now()
                )
                
                if coupon.max_uses > 0 and coupon.current_uses >= coupon.max_uses:
                    return Response({'error': 'Coupon usage limit reached'}, status=status.HTTP_400_BAD_REQUEST)
                
                if coupon.discount_type == 'percentage':
                    amount = amount * (1 - coupon.discount_value / 100)
                else:
                    amount = max(0, amount - float(coupon.discount_value))
                
            except Coupon.DoesNotExist:
                return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'course_id': course.id,
                    'user_id': request.user.id,
                }
            )
            
            # Create transaction record
            transaction = Transaction.objects.create(
                user=request.user,
                course=course,
                amount=amount,
                stripe_payment_intent_id=intent.id,
                status='pending'
            )
            
            return Response({
                'client_secret': intent.client_secret,
                'transaction_id': transaction.id
            })
            
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        transaction_id = request.data.get('transaction_id')
        payment_intent_id = request.data.get('payment_intent_id')
        
        transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
        
        try:
            # Verify payment with Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                transaction.status = 'completed'
                transaction.completed_at = timezone.now()
                transaction.stripe_charge_id = intent.charges.data[0].id if intent.charges.data else ''
                transaction.save()
                
                # Enroll user in course
                Enrollment.objects.get_or_create(
                    student=request.user,
                    course=transaction.course
                )
                
                return Response({'status': 'success', 'message': 'Payment successful'})
            else:
                transaction.status = 'failed'
                transaction.save()
                return Response({'error': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
                
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Update transaction status
            try:
                transaction = Transaction.objects.get(stripe_payment_intent_id=payment_intent['id'])
                transaction.status = 'completed'
                transaction.completed_at = timezone.now()
                transaction.save()
            except Transaction.DoesNotExist:
                pass
        
        return Response(status=status.HTTP_200_OK)


class MyTransactionsView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class CreateSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        plan = request.data.get('plan')  # 'monthly' or 'yearly'
        
        if plan not in ['monthly', 'yearly']:
            return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)
        
        price_id = settings.STRIPE_MONTHLY_PRICE_ID if plan == 'monthly' else settings.STRIPE_YEARLY_PRICE_ID
        
        try:
            # Create or retrieve Stripe customer
            customer = stripe.Customer.create(
                email=request.user.email,
                metadata={'user_id': request.user.id}
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
            )
            
            # Save subscription record
            Subscription.objects.create(
                user=request.user,
                plan=plan,
                stripe_subscription_id=subscription.id,
                stripe_customer_id=customer.id,
                current_period_start=timezone.datetime.fromtimestamp(subscription.current_period_start),
                current_period_end=timezone.datetime.fromtimestamp(subscription.current_period_end),
                status='active'
            )
            
            return Response({'status': 'success', 'subscription_id': subscription.id})
            
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CouponValidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code')
        course_id = request.data.get('course_id')
        
        try:
            coupon = Coupon.objects.get(
                code=code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now()
            )
            
            if coupon.max_uses > 0 and coupon.current_uses >= coupon.max_uses:
                return Response({'error': 'Coupon usage limit reached'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if coupon is applicable to the course
            if coupon.applicable_courses.exists() and course_id:
                if not coupon.applicable_courses.filter(id=course_id).exists():
                    return Response({'error': 'Coupon not applicable to this course'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CouponSerializer(coupon)
            return Response(serializer.data)
            
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)
```
