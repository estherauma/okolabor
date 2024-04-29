import unittest
from unittest.mock import patch
from common.email import EmailHelper

class EmailTestCase(unittest.TestCase):
    @patch('common.email.send_mail')
    @patch('common.email.render_to_string')
    def test_send_email_without_template(self, mock_render, mock_send_mail):
        # Arrange
        to_emails = ['test@example.com']
        subject = 'Test Subject'
        body = 'Test Body'
        from_email = 'noreply@example.com'

        # Act
        mailer = EmailHelper()
        result = mailer.send_email(to_emails, subject, body, from_email=from_email)

        # Assert
        mock_send_mail.assert_called_once_with(subject, body, from_email, to_emails)
        self.assertTrue(result)

    @patch('common.email.send_mail')
    @patch('common.email.render_to_string')
    def test_send_email_with_template(self, mock_render, mock_send_mail):
        # Arrange
        to_emails = ['test@example.com']
        subject = 'Test Subject'
        body = 'Test Body'
        template = 'template_name'
        from_email = 'noreply@example.com'

        # Act
        mailer = EmailHelper()
        result = mailer.send_email(to_emails, subject, body, template=template, from_email=from_email)

        # Assert
        mock_render.assert_called_once_with('emails/template_name', {"body": body})
        mock_send_mail.assert_called_once()
        self.assertTrue(result)

    @patch('common.email.send_mail')
    @patch('common.email.render_to_string')
    def test_send_email_exception(self, mock_render, mock_send_mail):
        # Arrange
        to_emails = ['test@example.com']
        subject = 'Test Subject'
        body = 'Test Body'
        template = 'template_name'
        from_email = 'noreply@example.com'
        mock_send_mail.side_effect = Exception('Test Exception')

        # Act
        mailer = EmailHelper()
        result = mailer.send_email(to_emails, subject, body, template=template, from_email=from_email)

        # Assert
        mock_render.assert_called_once_with('emails/template_name', {"body": body})
        mock_send_mail.assert_called_once()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
