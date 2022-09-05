from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "name",)

class ResetPasswordCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetPasswordCode
        fields = ("code",)
        