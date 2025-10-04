from fastapi import Depends

from shortener.infra.settings import get_settings
from shortener.infra.services.sendgrid_email import SendGridEmailService


def make_sendgrid_email_service():
    return SendGridEmailService()


def get_send_email_service():
    match get_settings().send_email_service_impl:
        case "sendgrid":
            dep_func = make_sendgrid_email_service
        case _:
            dep_func = make_sendgrid_email_service
    return Depends(dep_func)