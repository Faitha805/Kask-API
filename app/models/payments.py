from app.extensions import db
from datetime import datetime

class Payment(db.Model):
    # Customizing the table name
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    payment_date = db.Column(db.DateTime, default = datetime.now())
    amount = db.Column(db.Float, nullable = False)
    payment_method = db.Column(db.String(50)) # These include but not limited to Cash, Mobile Money, Bank
    payment_status = db.Column(db.String(20), default = "Paid") # These can be Paid, Pending or Failed.
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id")) # Reference to parent, bookings.
    booking = db.relationship("User", backref="payments")
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    # Attribute definition for new objects.
    def __init__(self, payment_date, amount, payment_method, payment_status, booking_id):
        super(Payment, self).__init__()
        self.payment_date = payment_date
        self.amount = amount
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.booking_id = booking_id

    # Payement epresentation
    def __repr__(self):
        return f"{self.payment_status} {self.amount}"