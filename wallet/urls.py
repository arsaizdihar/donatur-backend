from django.urls import path

from .views import TopUpRequestView, TopUpVerifyView

urlpatterns = [
    path("topup/", TopUpRequestView.as_view(), name="topup"),
    path("topup/requests/", TopUpVerifyView.as_view(), name="topup-verify")
]
