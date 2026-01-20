from abc import ABC, abstractmethod

class EmailProvider(ABC):

    @abstractmethod
    def fetch_recent_emails(self, db, user_id: int):
        pass

    @abstractmethod
    def send_email(
        self,
        db,
        user_id: int,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str = None,
    ):
        pass
