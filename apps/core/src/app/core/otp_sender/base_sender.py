from abc import ABC, abstractmethod

from app.models.user import User


class BaseOTPSender(ABC):

    @abstractmethod
    def send(self, otp: str, receiver: User):
        pass
