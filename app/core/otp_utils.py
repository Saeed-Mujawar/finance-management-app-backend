import random
import string
import yagmail

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

async def send_otp_email(to_email, otp):
    yag = yagmail.SMTP('saeedmujawar2000@gmail.com', 'slml qtvp mksg zkol')
    subject = 'Your OTP for Finance App Signup'
    content = f'Your OTP for Finance App signup is: {otp}'
    yag.send(to=to_email, subject=subject, contents=content)
