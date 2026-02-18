from django.db import models

GENDER_CHOICES = [
    ("Male", "Male"),
    ("Female", "Female"),
]

BRANCH_CHOICES = [
    ("CSE", "CSE"),
    ("ECE", "ECE"),
    ("IT", "IT"),
    ("EEE", "EEE"),
    ("ME", "ME"),
    ("CE", "CE"),
    ("CSIT", "CSIT"),
    ("AIML", "AIML"),
    ("OTHERS", "OTHERS"),
]

YEAR_CHOICES = [("1", "1st"), ("2", "2nd")]

TEAM_TYPE = [("solo", "solo"), ("duo", "duo")]


class Team(models.Model):
    team_id = models.CharField(max_length=50, unique=True)
    team_type = models.CharField(max_length=10, choices=TEAM_TYPE)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.team_id


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")

    name = models.CharField(max_length=40)
    phone = models.CharField(max_length=10)
    student_no = models.CharField(max_length=20, unique=True,db_index=True)
    roll_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    attendance = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)

    def __str__(self):
        return self.name

class Payment(models.Model):
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)

    amount = models.IntegerField()
    team_type = models.CharField(max_length=10)

    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.razorpay_order_id