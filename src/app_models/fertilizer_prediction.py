from db import db
from sqlalchemy.sql import func


class FertilizerPrediction(db.Model):
    __tablename__ = "fertilizer_predictions"

    prediction_id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    temperature = db.Column(db.Numeric(5, 2), nullable=False)

    humidity = db.Column(db.Numeric(5, 2), nullable=False)

    moisture = db.Column(db.Numeric(5, 2), nullable=False)

    soil_type_id = db.Column(
        db.Integer,
        db.ForeignKey("soil_types.soil_type_id"),
        nullable=False
    )

    crop_type_id = db.Column(
        db.Integer,
        db.ForeignKey("crops.crop_id"),
        nullable=False
    )

    nitrogen = db.Column(db.Numeric(6, 2), nullable=False)

    potassium = db.Column(db.Numeric(6, 2), nullable=False)

    phosphorous = db.Column(db.Numeric(6, 2), nullable=False)

    predicted_fertilizer_id = db.Column(
        db.Integer,
        db.ForeignKey("fertilizers.fertilizer_id"),
        nullable=False
    )

    prediction_time = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now()
    )
    