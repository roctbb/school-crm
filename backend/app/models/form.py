from app.database import db
from app.tables import form_visibility_roles
from app.tables import form_category_entity

class FormCategory(db.Model):
    __tablename__ = 'form_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)

    target_entities = db.relationship(
        'EntityType',
        secondary=form_category_entity,
        backref=db.backref('form_categories', lazy='dynamic'),
        lazy='dynamic'
    )


class Form(db.Model):
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    questions = db.Column(db.JSON)
    category_id = db.Column(db.Integer, db.ForeignKey('form_categories.id', ondelete='SET NULL'), nullable=True)
    category = db.relationship('FormCategory', backref=db.backref('forms', lazy=True))
    visible_for = db.relationship('Role', secondary=form_visibility_roles, backref=db.backref('forms', lazy=True))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
