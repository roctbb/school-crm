from app.database import db
from app.tables import entity_submission, entity_children


class EntityType(db.Model):
    __tablename__ = 'entity_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Entity(db.Model):
    __tablename__ = 'entities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('entity_types.id', ondelete='CASCADE'), nullable=False)
    type = db.relationship('EntityType', backref=db.backref('entities', lazy=True))

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    owner = db.relationship('User', backref=db.backref('entities', lazy=True))

    submissions = db.relationship('FormSubmission', secondary=entity_submission, backref=db.backref('entities', lazy=True))

    children = db.relationship('Entity', secondary=entity_children,
                               primaryjoin=id == entity_children.c.parent_id,
                               secondaryjoin=id == entity_children.c.child_id,
                               backref=db.backref('parents', lazy=True))
    invite_code = db.Column(db.String(50), unique=True, nullable=True)
