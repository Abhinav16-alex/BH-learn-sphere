```python
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Badge, UserBadge

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'role', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    earned_badges = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 
                  'profile_picture', 'bio', 'points', 'date_of_birth', 'phone_number',
                  'date_joined', 'earned_badges']
        read_only_fields = ['id', 'date_joined', 'points']
    
    def get_earned_badges(self, obj):
        badges = UserBadge.objects.filter(user=obj).select_related('badge')
        return BadgeSerializer([ub.badge for ub in badges], many=True).data


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = '__all__'
```
