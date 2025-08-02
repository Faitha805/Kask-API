from app.extensions import db
from datetime import datetime

class Message(db.Model):
    # Customizing the table name.
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    time_stamp = db.Column(db.DateTime, default=datetime.now())
    edited_at = db.Column(db.DateTime, onupdate=datetime.now())


    def __init__(self, sender_id, recipient_id, content, time_stamp):
        super(Message, self).__init__()
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.content = content
        self.time_stamp = time_stamp

    # Representation of a called message with it's sender id
    def __repr__(self) -> str:# String formating
         return f"Message from user with id {self.sender_id}, sent at {self.time_stamp}"  