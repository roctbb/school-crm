from app.database import db

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), nullable=False)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False)
    entity = db.relationship('Entity', backref=db.backref('comments', lazy=True))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

