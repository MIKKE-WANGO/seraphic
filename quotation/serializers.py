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
    

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("title","budget", "guests", "date")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class CapacitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Capacity
        fields = ('restaurant', 'theatre')

