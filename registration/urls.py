from django.urls import path
from .views import MarkAttendance, RegisterTeam , VerifyPayment, CreateOrder

urlpatterns = [
    path("register/", RegisterTeam.as_view()),
    path("attendance/", MarkAttendance.as_view()),
    path("create-order/", CreateOrder.as_view()),
    path("verify-payment/", VerifyPayment.as_view())
]
