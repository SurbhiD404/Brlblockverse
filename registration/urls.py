from django.urls import path
from .views import MarkAttendance, RegisterTeam

urlpatterns = [
    path("register/", RegisterTeam.as_view()),
    path("attendance/", MarkAttendance.as_view())
]
