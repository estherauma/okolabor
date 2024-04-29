
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decouple import config


class EmailHelper:

    @classmethod
    def send_email(cls, to_emails, subject, body, template=None, from_email=config("APPLICATION_FROM_EMAIL")):
        try:
            if template is None:
                return send_mail(subject, body, from_email, to_emails)

            html_message = render_to_string(f'emails/{template}', {"body": body})
            plain_message = strip_tags(html_message)

            # Wrap in try-catch and show error message
            send_mail(subject, plain_message, from_email, to_emails, html_message=html_message)
            return True  # Email sent successfully
        except Exception as e:
            # Handle the exception and log or display an error message
            # TODO: Send to sentry
            print(e)
            return False  # Email sending failed
