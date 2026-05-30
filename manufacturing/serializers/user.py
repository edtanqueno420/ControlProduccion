# manufacturing/serializers/user.py — actualizar UserSerializer
from rest_framework import serializers
from django.contrib.auth.models import User

from manufacturing.models import Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Profile
        fields = ['role']


class RegisterSerializer(serializers.Serializer):
    username  = serializers.CharField(max_length=150)
    email     = serializers.EmailField()
    password  = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(write_only=True)
    role      = serializers.ChoiceField(
        choices=['ADMIN', 'SUPERVISOR', 'OPERARIO'],
        default='OPERARIO',
    )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        role = validated_data.pop('role', 'OPERARIO')
        validated_data.pop('password2')
        is_staff = role in ['ADMIN', 'SUPERVISOR']
        user = User.objects.create_user(**validated_data, is_staff=is_staff)
        Profile.objects.create(user=user, role=role)
        return user


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    num_orders = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined', 'profile', 'num_orders',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_num_orders(self, obj):
        return obj.production_orders.count()


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']

    def validate_email(self, value):
        request = self.context.get('request')
        if User.objects.filter(email=value).exclude(pk=request.user.pk).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(min_length=8, write_only=True)
    new_password2    = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Passwords do not match.'})
        return data
