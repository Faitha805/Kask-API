from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users" # Changing the table name from Users(model name by default) to users.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(250), nullable=True)
    password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), default="Customer")
    email_preferences = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, name, email, phone, address, password, user_type):
        super(User, self).__init__()
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password
        self.user_type = user_type
