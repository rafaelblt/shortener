from shortener.infra.services.sendgrid_email import SendGridEmailService


def make_sendgrid_email_service():
    return SendGridEmailService()
