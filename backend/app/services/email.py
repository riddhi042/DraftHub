# backend/app/services/email.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.settings import get_settings

settings = get_settings()


def _send(to_email: str, subject: str, html: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"DraftHub <{settings.gmail_user}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(settings.gmail_user, settings.gmail_app_password)
            server.sendmail(settings.gmail_user, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_verification_email(to_email: str, username: str, token: str) -> bool:
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 24px;">
        <div style="margin-bottom: 32px;">
            <span style="background: #2563eb; color: white; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 14px;">DraftHub</span>
        </div>
        <h1 style="font-size: 22px; font-weight: 600; color: #111827; margin-bottom: 8px;">
            Verify your email
        </h1>
        <p style="color: #6b7280; font-size: 14px; margin-bottom: 28px;">
            Hi {username}, click the button below to verify your DraftHub account.
        </p>
        <a href="http://localhost:5173/verify?token={token}"
           style="display: inline-block; background: #2563eb; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 14px;">
            Verify Email
        </a>
        <p style="color: #9ca3af; font-size: 12px; margin-top: 28px;">
            This link expires in 24 hours. If you didn't create an account, ignore this email.
        </p>
    </div>
    """
    return _send(to_email, "Verify your DraftHub account", html)


def send_welcome_email(to_email: str, username: str) -> bool:
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 24px;">
        <div style="margin-bottom: 32px;">
            <span style="background: #2563eb; color: white; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 14px;">DraftHub</span>
        </div>
        <h1 style="font-size: 22px; font-weight: 600; color: #111827; margin-bottom: 8px;">
            Welcome to DraftHub, {username}!
        </h1>
        <p style="color: #6b7280; font-size: 14px; margin-bottom: 28px;">
            Your account is verified. Start managing your blueprints and collaborating with your team.
        </p>
        <a href="http://localhost:5173/dashboard"
           style="display: inline-block; background: #2563eb; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 14px;">
            Go to Dashboard
        </a>
    </div>
    """
    return _send(to_email, "Welcome to DraftHub", html)