import re
from django.db import transaction
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Team, Player


name_regex = r"^[A-Za-z ]{3,40}$"
digits_regex = r"^\d+$"


def validate_student_no(value):
    if not value.startswith(("23", "24", "25")):
        raise serializers.ValidationError(
            "Student number must start with 23, 24 or 25"
        )
    return value


def validate_roll_no(value):
    if not value.startswith(("23", "24", "25")):
        raise serializers.ValidationError(
            "Roll number must start with 23, 24 or 25"
        )
    return value

def validate_college_email(name, student_no, email):
    first_name = name.split()[0].lower()
    expected = f"{first_name}{student_no}@akgec.ac.in"
    if email.lower() != expected:
        raise serializers.ValidationError(
            f"Email must be {expected}"
        )


class PlayerInputSerializer(serializers.Serializer):
    name = serializers.RegexField(name_regex)
    phone = serializers.RegexField(r"^[6-9]\d{9}$")
    student_no = serializers.RegexField(digits_regex, validators=[validate_student_no])
    roll_no = serializers.RegexField(digits_regex, validators=[validate_roll_no])
    email = serializers.EmailField()
    year = serializers.ChoiceField(choices=["1", "2"])
    gender = serializers.CharField()
    branch = serializers.CharField()
    
    
    def validate_student_no(self, value):
        if Player.objects.filter(student_no=value).exists():
            raise serializers.ValidationError("Student no already registered")
        return value

    def validate_roll_no(self, value):
        if Player.objects.filter(roll_no=value).exists():
            raise serializers.ValidationError("Roll number already registered")
        return value
    
    
    def validate_email(self, value):
        if Player.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    
    def validate(self, data):
        validate_college_email(data["name"], data["student_no"], data["email"])
        return data


class TeamSerializer(serializers.Serializer):
    teamId = serializers.CharField()
    team_type = serializers.ChoiceField(choices=["solo", "duo"])
    password = serializers.CharField( min_length=6)

    player1 = PlayerInputSerializer()
    player2 = PlayerInputSerializer(required=False)

    def validate(self, data):
        team_id = data["teamId"]
        team_type = data["team_type"]
        has_player2 = "player2" in data

        
        if Team.objects.filter(team_id=team_id).exists():
            raise serializers.ValidationError(
                {"teamId": "Team ID already registered"}
            )

        
        if team_type == "solo" and has_player2:
            raise serializers.ValidationError(
                "Solo team cannot have player2"
            )    
    
        if team_type == "duo" and not has_player2:
            raise serializers.ValidationError(
                "Duo team requires player2"
            )

        return data


    @transaction.atomic 
    def create(self, validated_data):
        raw_password = validated_data.pop("password")
        
        
        team = Team.objects.create(
            team_id=validated_data["teamId"],
            team_type=validated_data["team_type"],
            password_hash=make_password(raw_password),
        )

        Player.objects.create(team=team, **validated_data["player1"])

        if validated_data["team_type"] == "duo":
            Player.objects.create(team=team, **validated_data["player2"])

        return team
