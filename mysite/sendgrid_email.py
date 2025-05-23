#!/usr/bin/env python3  # Use this for CGI scripts
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Debugging: Check if the API key is retrieved correctly


message = Mail(
    from_email='handelgakuru@gmail.com',
    to_emails='seasmotorsgarage@gmail.com',
    subject='Password Reset Request',
    html_content='<strong>Your password reset token is: 123456</strong>'
)

try:
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.body}")
    print(f"Headers: {response.headers}")
except Exception as e:
    print(f"Error: {e}")
