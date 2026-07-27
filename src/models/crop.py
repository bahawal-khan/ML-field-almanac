from database import db


class Crop(db.Model):
    __tablename__ = "crops"

    crop_id = db.Column(
        db.Integer,
        primary_key=True
    )

    crop_name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return f"<Crop {self.crop_name}>"