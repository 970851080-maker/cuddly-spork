from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def send_email(subject: str, body: str) -> None:
    host = os.environ["NEWS_DAILY_SMTP_HOST"]
    port = int(os.environ.get("NEWS_DAILY_SMTP_PORT", "465"))
    user = os.environ["NEWS_DAILY_SMTP_USER"]
    password = os.environ["NEWS_DAILY_SMTP_PASS"]
    to = os.environ["NEWS_DAILY_EMAIL_TO"]
    from_addr = os.environ.get("NEWS_DAILY_EMAIL_FROM", user)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to
    msg.set_content(body)

    if port == 465:
        with smtplib.SMTP_SSL(host, port) as s:
            s.login(user, password)
            s.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            s.login(user, password)
            s.send_message(msg)

