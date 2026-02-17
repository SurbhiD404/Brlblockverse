import qrcode
from io import BytesIO
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def qr(student_no):
    img = qrcode.make(student_no)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0) 
    return buffer

def send_registration_mail(team, raw_password):
    for p in team.players.all():

        qr_img = qr(p.student_no)

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>

<body style="margin:0;padding:0;background:#eef2f7;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:20px;">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0"
style="max-width:600px;background:#ffffff;border-radius:14px;overflow:hidden;
box-shadow:0 6px 16px rgba(0,0,0,0.08);">

<!-- Header -->
<tr>
<td style="background:linear-gradient(135deg,#4CAF50,#2e7d32);
padding:28px;text-align:center;color:white;">
<h1 style="margin:0;font-size:28px;">🎉 Welcome to BLOCKVERSE’26</h1>
<p style="margin:8px 0 0;font-size:16px;">
Your journey into innovation begins now
</p>
</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:30px;font-size:16px;line-height:1.7;color:#333;">

<p>Dear <b>{p.name}</b>,</p>

<p>
Congratulations! You are officially registered for
<b>BLOCKVERSE’26</b> — one of the most awaited
technical experiences of the year 🚀
</p>

<p>
This is more than an event — it’s a stage to showcase
your ideas, creativity, teamwork, and brilliance.
We’re excited to have you onboard!
</p>

<table width="100%" cellpadding="14" cellspacing="0"
style="background:#f7f9fb;border-radius:10px;margin:20px 0;font-size:15px;">
<tr><td><b>Team ID:</b> {team.team_id}</td></tr>
<tr><td><b>Password:</b> {raw_password}</td></tr>
</table>

<p>
📍 <b>Payment:</b> BRL LAB (5th floor CSIT) after 4 PM
</p>

<p>
Please keep your QR safe — it will be scanned at entry
for attendance and verification.
</p>

<p>
Prepare for challenges, fun, collaboration,
and unforgettable memories ✨<br>
BLOCKVERSE is not just participation —
it’s an experience.
</p>

<p style="margin-top:28px;">
With excitement and best wishes,<br>
<b>BRL Technical Society ❤️</b>
</p>

</td>
</tr>

<!-- Footer -->
<tr>
<td style="background:#eef2f7;text-align:center;padding:16px;
font-size:13px;color:#666;">
See you at BLOCKVERSE’26 • Let’s build the future together
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

        email = EmailMultiAlternatives(
            subject="🎟 BLOCKVERSE’26 Registration Confirmed — Welcome!",
            body="Registration successful",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[p.email],
        )

        email.attach_alternative(html, "text/html")
        email.attach("qr.png", qr_img.read(), "image/png")
        email.send()
