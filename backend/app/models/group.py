from app.database import db


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    type = db.Column(db.String(256), nullable=False)
    icon = db.Column(db.String(256), nullable=True)

    # Много ко многим с Entity через таблицу group_entity
    participants = db.relationship('Entity', secondary='group_entity', backref=db.backref('groups', lazy=True))

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    owner = db.relationship('User', backref=db.backref('groups', lazy=True))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
