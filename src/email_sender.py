"""
email_sender.py
-----------------
Sends the generated payslip PDF to each employee via email.

Credentials are NEVER hardcoded — they are read from environment
variables (loaded from a local .env file via python-dotenv). See
README.md for setup instructions.
"""

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

# Load variables from a .env file in the project root, if present.
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


class EmailConfigError(Exception):
    """Raised when required email environment variables are missing."""
    pass


def _validate_config():
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise EmailConfigError(
            "SENDER_EMAIL and/or SENDER_PASSWORD environment variables are not set. "
            "Create a .env file based on .env.example before sending emails."
        )


def send_payslip_email(employee: dict, pdf_path: str, month: str, year: str, to_email: str = None) -> str:
    """
    Email the payslip PDF to one employee.

    Args:
        employee: dict with at least Name and Email
        pdf_path: path to the PDF file to attach
        month, year: used in the subject/body text

    Returns:
        "Sent" on success, or a short error description on failure.
        (We return a string rather than raising so that a single failed
        email doesn't stop the whole batch run — see main.py.)
    """
    try:
        _validate_config()

        recipient = to_email if to_email else employee.get("Email")
        
        if not recipient or not isinstance(recipient, str) or "@" not in recipient:
            return "Failed: invalid or missing email address"

        if not os.path.exists(pdf_path):
            return "Failed: PDF file not found"

        msg = EmailMessage()
        msg["Subject"] = f"Payslip for {month} {year} - {employee.get('Employee_Name', '')}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient
        msg.set_content(
            f"Dear {employee.get('Employee_Name', 'Employee')},\n\n"
            f"Please find attached your payslip for {month} {year}.\n\n"
            f"Net Pay: Rs. {employee.get('NetPay', 'N/A')}\n\n"
            "This is an automated email. Please do not reply.\n\n"
            "Regards,\nHR & Payroll Team"
        )

        with open(pdf_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(pdf_path),
            )

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        return "Sent"

    except EmailConfigError as e:
        return f"Failed: {e}"
    except smtplib.SMTPAuthenticationError:
        return "Failed: SMTP authentication error (check SENDER_EMAIL/SENDER_PASSWORD)"
    except smtplib.SMTPException as e:
        return f"Failed: SMTP error ({e})"
    except Exception as e:
        return f"Failed: {e}"
