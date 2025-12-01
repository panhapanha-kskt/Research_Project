from sqlalchemy import Column, Integer, String
from .db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email_enc = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

    def as_dict(self, decrypt_fn=None):
        email = self.email_enc
        if decrypt_fn:
            try:
                email = decrypt_fn(self.email_enc)
            except Exception:
                email = "<decryption-error>"

        return {
            "id": self.id,
            "name": self.name,
            "email": email,
            "age": self.age
        }
