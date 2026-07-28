from db import db
from sqlalchemy.sql import func


class CropPrediction(db.Model):
    __tablename__ = "crop_predictions"

    prediction_id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    nitrogen = db.Column(db.Numeric(6, 2), nullable=False)

    phosphorus = db.Column(db.Numeric(6, 2), nullable=False)

    potassium = db.Column(db.Numeric(6, 2), nullable=False)

    temperature = db.Column(db.Numeric(5, 2), nullable=False)

    humidity = db.Column(db.Numeric(5, 2), nullable=False)

    ph = db.Column(db.Numeric(4, 2), nullable=False)

    rainfall = db.Column(db.Numeric(7, 2), nullable=False)

    predicted_crop_id = db.Column(
        db.Integer,
        db.ForeignKey("crops.crop_id"),
        nullable=False
    )

    prediction_time = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now()
    )