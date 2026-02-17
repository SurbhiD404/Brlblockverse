from django.shortcuts import render
from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TeamSerializer
from .utils import send_registration_mail
from .models import Team, Player
from django.conf import settings

class RegisterTeam(APIView):

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        try:
            with transaction.atomic():
              team = serializer.save()
              send_registration_mail(team, request.data["password"])
            
        except IntegrityError:
            return Response(
                {"success": False,
                "error": "Duplicate entry: team ID / student no / roll no already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # except Exception as e:
        #     return Response(
        #         {"success": False, "error": str(e)},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )    
        
        return Response({
            "success": True,
            "team_id": team.team_id,
            "team_type": team.team_type,
            "message": "Registration successful. Confirmation email sent."
        }, status=status.HTTP_201_CREATED)


class MarkAttendance(APIView): 

    def post(self, request):
        
        if request.headers.get("X-SCANNER-KEY") != settings.SCANNER_SECRET:
            return Response({"error": "Unauthorized"}, status=403)
        
        student_no = request.data.get("student_no")

        if not student_no:
            return Response(
                {"error": "student_no required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
             # player = Player.objects.get(student_no=student_no)
                player = Player.objects.select_for_update().get(student_no=student_no)

                if player.attendance:
                    return Response({
                        "error": "Already marked",
                        "name": player.name
                    }, status=status.HTTP_400_BAD_REQUEST)

                player.attendance = True
                player.save()

                return Response({
                    "success": True,
                    "name": player.name,
                    "team": player.team.team_id
                })

        except Player.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)
           