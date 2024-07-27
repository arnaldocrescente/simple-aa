from abc import ABC, abstractmethod

from app.models.user import User


class BaseOTP(ABC):

    @abstractmethod
    def generate(self, user: User):
        pass
