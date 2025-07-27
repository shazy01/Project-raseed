from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReceiptViewSet, WalletPassViewSet, UserQueryViewSet, SpendingAnalysisViewSet

router = DefaultRouter()
router.register(r'receipts', ReceiptViewSet)
router.register(r'walletpasses', WalletPassViewSet)
router.register(r'queries', UserQueryViewSet)

router.register(r'spendinganalysis', SpendingAnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]
