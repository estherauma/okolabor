
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decouple import config


class EmailHelper:

    @classmethod
    def send_email(cls, to_emails, subject, body, template=None, from_email=config("APPLICATION_FROM_EMAIL")):
        try:
            if template is None:
                # Convert the body dictionary to a string representation if it's a dict
                if isinstance(body, dict):
                    body = "\n".join([f"{key}: {value}" for key, value in body.items()])
                print(f"Email sent to without template {to_emails}")
                return send_mail(subject, body, from_email, to_emails)

            # Render the email template
            html_message = render_to_string(f'emails/{template}', {"body": body})
            plain_message = strip_tags(html_message)

            send_mail(subject, plain_message, from_email, to_emails, html_message=html_message)
            print(f"Email sent to {to_emails}")
            return True  # Email sent successfully
        except Exception as e:
            # Handle the exception and log or display an error message
            print(e)
            return False  # Email sending failed
