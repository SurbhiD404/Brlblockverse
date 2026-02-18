from django.shortcuts import render
from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import TeamSerializer
from .utils import send_registration_mail
from .models import Team, Player, Payment
from .razorpay_client import client

class CreateOrder(APIView):

    def post(self, request):

        team_type = request.data.get("team_type")

        if team_type not in ["solo", "duo"]:
            return Response({"error": "Invalid team type"}, status=400)

        amount = settings.SOLO_FEE if team_type == "solo" else settings.DUO_FEE

        try:
            order = client.order.create({
                "amount": amount * 100,
                "currency": "INR",
                "payment_capture": 1
            })

            Payment.objects.create(
                razorpay_order_id=order["id"],
                amount=amount,
                team_type=team_type
            )

            return Response({
                "order_id": order["id"],
                "amount": amount,
                "key": settings.RAZORPAY_KEY_ID
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)





class VerifyPayment(APIView):

    def post(self, request):

        order_id = request.data.get("razorpay_order_id")
        payment_id = request.data.get("razorpay_payment_id")
        signature = request.data.get("razorpay_signature")
        team_data = request.data.get("team_data")

        if not all([order_id, payment_id, signature, team_data]):
            return Response({"error": "Missing fields"}, status=400)

        try:
            payment = Payment.objects.get(razorpay_order_id=order_id)

            if payment.verified:
                return Response({"error": "Payment already verified"}, status=400)

            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })

        except Payment.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        except Exception:
            return Response({"error": "Signature verification failed"}, status=400)

        try:
            with transaction.atomic():

                serializer = TeamSerializer(data=team_data)
                serializer.is_valid(raise_exception=True)
                team = serializer.save()

                payment.razorpay_payment_id = payment_id
                payment.razorpay_signature = signature
                payment.verified = True
                payment.save()

                send_registration_mail(team, team_data["password"])

        except IntegrityError:
            return Response({
                "error": "Duplicate entry: team/student already exists"
            }, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "success": True,
            "team_id": team.team_id,
            "message": "Payment verified & registration successful"
        })



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
           