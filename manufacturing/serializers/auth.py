# manufacturing/serializers/auth.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email']    = user.email
        token['role']     = user.profile.role if hasattr(user, 'profile') else 'OPERARIO'
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id']  = self.user.id
        data['username'] = self.user.username
        data['email']    = self.user.email
        data['role']     = self.user.profile.role if hasattr(self.user, 'profile') else 'OPERARIO'
        data['is_staff'] = self.user.is_staff
        return data


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
