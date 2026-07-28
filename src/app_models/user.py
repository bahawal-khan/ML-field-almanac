from db import db
from sqlalchemy.sql import func


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.BigInteger, primary_key=True)

    username = db.Column(db.String(50), nullable=False)

    email = db.Column(db.String(255), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    

    def __repr__(self):
        return f"<User {self.username}>"