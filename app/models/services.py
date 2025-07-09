from app.extensions import db
from datetime import datetime

class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False) # Swimming pool, grounds, conference hall and restaurant.
    service_name = db.Column(db.String(100), unique=True) # Children's pool, adult's pool, main grounds, footbal pitch, conference hall, restaurant.
    description = db.Column(db.String(250), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    availability_status = db.Column(db.String(20), default="Available", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, service_type, service_name, description, price_per_hour, availability_status):
        super(Service, self).__init__()
        self.service_type = service_type
        self.service_name = service_name
        self.description = description
        self.price_per_hour = price_per_hour
        self.availability_status = availability_status