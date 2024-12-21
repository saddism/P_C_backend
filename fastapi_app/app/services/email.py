import aiosmtplib
from email.mime.text import MIMEText
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SMTP_PASSWORD = getenv("SMTP_PASSWORD")
if not SMTP_PASSWORD:
    raise ValueError("SMTP_PASSWORD environment variable is not set")

async def send_verification_email(to_email: str, code: str):
    """
    Send verification email using Alibaba Cloud SMTP service.

    Args:
        to_email: Recipient email address
        code: 6-digit verification code
    """
    message = MIMEText(f"Your verification code is: {code}")
    message["From"] = "welcome@guixian.cn"
    message["To"] = to_email
    message["Subject"] = "Email Verification"

    try:
        await aiosmtplib.send(
            message,
            hostname="smtpdm.aliyun.com",
            port=465,
            use_tls=True,
            username="welcome@guixian.cn",
            password=SMTP_PASSWORD
        )
    except Exception as e:
        # Log error but don't expose SMTP details in error message
        print(f"Failed to send email: {str(e)}")
        raise ValueError("Failed to send verification email")
