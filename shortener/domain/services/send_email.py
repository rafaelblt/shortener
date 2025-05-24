from abc import ABC, abstractmethod


class SendEmailService(ABC):

    @abstractmethod
    async def send_email(self, receiver: str, subject: str, body: str):
        pass
