from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("users", views.UserViewSet)
router.register("ledgers", views.LedgerViewSet)
router.register("ledger_access", views.LedgerAccessViewSet)
router.register("records", views.RecordViewSet)
router.register("receipts", views.ReceiptViewSet)
router.register("sharepay", views.SharePayViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
