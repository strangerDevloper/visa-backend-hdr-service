# app/helpers/email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.sender_email = settings.SENDER_EMAIL

    def send_vendor_approval_email(self, to_email: str, password: str):
        subject = "Your Vendor Account Has Been Approved"
        body = f"""
        <html>
            <body>
                <h2>Welcome to Our Visa Portal</h2>
                <p>Your vendor account has been approved.</p>
                <p>Here are your login credentials:</p>
                <ul>
                    <li><strong>Email:</strong> {to_email}</li>
                    <li><strong>Temporary Password:</strong> {password}</li>
                </ul>
                <p>Please change your password after first login.</p>
                <p>Best regards,<br>Vendor Management Team</p>
            </body>
        </html>
        """

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            logger.info(f"Approval email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send approval email. Vendor was approved but email failed."
            )

# Singleton instance
email_sender = EmailSender()