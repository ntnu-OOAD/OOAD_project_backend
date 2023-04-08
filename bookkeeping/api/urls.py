from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("users", views.UserViewSet)
router.register("ledgers", views.LedgerViewSet)
router.register("ledger_access", views.LedgerAccessViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
