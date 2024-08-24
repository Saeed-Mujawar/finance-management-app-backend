import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import asyncio

def generate_otp(length=6):
    import random
    import string
    return ''.join(random.choices(string.digits, k=length))

async def send_otp_email(to_email, otp):
    # Sender email and name
    sender_email = 'saeedmujawar2000@gmail.com'
    sender_name = 'Finance App OTP'
    
    # Email subject and content
    subject = 'Your OTP for Finance App Signup'
    content = f'Your OTP for Finance App signup is: {otp}'
    
    # Create MIME email object
    msg = MIMEMultipart()
    msg['From'] = formataddr((sender_name, sender_email))
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach the email content
    msg.attach(MIMEText(content, 'plain'))
    
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = sender_email
    smtp_password = 'slml qtvp mksg zkol'
    
    # Use asyncio to run the synchronous send function
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, send_email, smtp_server, smtp_port, smtp_user, smtp_password, msg)

def send_email(smtp_server, smtp_port, smtp_user, smtp_password, msg):
    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
