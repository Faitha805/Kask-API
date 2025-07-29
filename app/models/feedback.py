from app.extensions import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__ = "feedbacks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    message = db.Column(db. String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, name, phone_number, email, message): 
        super(Feedback, self).__init__()
        self.name = name
        self.phone_nimber = phone_number
        self.email = email
        self.message = message