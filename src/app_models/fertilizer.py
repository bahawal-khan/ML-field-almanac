from db import db


class Fertilizer(db.Model):
    __tablename__ = "fertilizers"

    fertilizer_id = db.Column(
        db.Integer,
        primary_key=True
    )

    fertilizer_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return f"<Fertilizer {self.fertilizer_name}>"