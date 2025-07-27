from rest_framework import serializers
from .models import Receipt, WalletPass, UserQuery

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'

class WalletPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletPass
        fields = '__all__'

class UserQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = '__all__'
