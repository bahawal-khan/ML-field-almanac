from db import db


class SoilType(db.Model):
    __tablename__ = "soil_types"

    soil_type_id = db.Column(
        db.Integer,
        primary_key=True
    )

    soil_name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return f"<SoilType {self.soil_name}>"