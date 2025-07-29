from app.extensions import db
from datetime import datetime

class Booking(db.Model):
    # Customizing the table name.
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    total_unit_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_status = db.Column(db.String(20), default='confirmed' , nullable=False) # The booking may be confirmed (upcoming), cancelled, missed or completed.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"))
    user = db.relationship('User', backref="bookings")
    service = db.relationship('Service', backref="bookings")
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, start_time, end_time, total_price, booking_date, booking_status, user_id, service_id):
        super(Booking, self).__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.total__unit_price = total_price
        self.booking_date = booking_date
        self.booking_status = booking_status
        self.user_id = user_id
        self.service_id = service_id

    # Reepresentation of a called booking with it's service id
    def __repr__(self) -> str:# Stringg formating
         return f"{self.booking_status} booking of service with id: {self.service_id}."  