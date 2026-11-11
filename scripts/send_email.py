"""Send a plain-text email to one or more recipients through Gmail SMTP.

Credentials are read from environment variables, never hard-coded:
    export SMTP_EMAIL="you@gmail.com"
    export SMTP_APP_PASSWORD="your-16-character-app-password"

Usage:
    python scripts/send_email.py "Subject" "Message body" person1@example.com person2@example.com
"""
import argparse
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def build_message(sender, recipients, subject, body):
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    return message


def send(sender, password, recipients, subject, body, host="smtp.gmail.com", port=587):
    message = build_message(sender, recipients, subject, body)
    with smtplib.SMTP(host, port, timeout=30) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, message.as_string())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("subject")
    parser.add_argument("body")
    parser.add_argument("recipients", nargs="+")
    args = parser.parse_args()

    sender = os.environ.get("SMTP_EMAIL")
    password = os.environ.get("SMTP_APP_PASSWORD")
    if not sender or not password:
        parser.error("Set SMTP_EMAIL and SMTP_APP_PASSWORD environment variables first")

    try:
        send(sender, password, args.recipients, args.subject, args.body)
        print(f"Email sent to {len(args.recipients)} recipient(s).")
    except smtplib.SMTPException as error:
        raise SystemExit(f"Failed to send email: {error}")


if __name__ == "__main__":
    main()
