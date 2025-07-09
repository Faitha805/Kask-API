from app.extensions import db
from datetime import datetime

class Gallery(db.Model):
    __tablename__ = "galleries"
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(250))
    caption = (db.Column(db.String(250), nullable=True))
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    service = db.relationship("Service", backref="galleries") # To access the parent entity which is services.
    created_at = db.Column(db.DateTime, default=datetime.now())# Back ref from seervices to the child entity, gallery.
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    # Constructoir for the gallery class to ensure that all new galleries have the necessary attributes.
    def __init__(self, image_url, caption, service_id):
        super(Gallery, self).__init__()
        self.image_url = image_url
        self.caption = caption
        self.service_id = service_id

    # Defininfg how the object will be represented when called.
    def __repr__(self):
        return f"{self.image_url} {self.caption}"