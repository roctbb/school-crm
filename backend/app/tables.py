
from app.database import db

user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

entity_submission = db.Table(
    'entity_submission',
    db.Column('entity_id', db.Integer, db.ForeignKey('entities.id', ondelete='CASCADE'), primary_key=True),
    db.Column('form_submission_id', db.Integer, db.ForeignKey('form_submissions.id', ondelete='CASCADE'),
              primary_key=True)
)

form_category_entity_type = db.Table(
    'form_category_entity_type',
    db.Column('form_category_id', db.Integer, db.ForeignKey('form_categories.id', ondelete='CASCADE'),
              primary_key=True),
    db.Column('type_id', db.Integer, db.ForeignKey('entity_types.id', ondelete='CASCADE'), primary_key=True)
)

form_visibility_roles = db.Table(
    'form_visibility_roles',
    db.Column('form_id', db.Integer, db.ForeignKey('forms.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

group_entity = db.Table(
    'group_entity',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
    db.Column('entity_id', db.Integer, db.ForeignKey('entities.id', ondelete='CASCADE'), primary_key=True)
)

entity_children = db.Table(
    'entity_children',
    db.Column('parent_id', db.Integer, db.ForeignKey('entities.id', ondelete='CASCADE'), primary_key=True),
    db.Column('child_id', db.Integer, db.ForeignKey('entities.id', ondelete='CASCADE'), primary_key=True)
)

form_category_entity = db.Table(
    'form_category_entity',
    db.Column('form_category_id', db.Integer, db.ForeignKey('form_categories.id', ondelete='CASCADE'),
              primary_key=True),
    db.Column('entity_type_id', db.Integer, db.ForeignKey('entity_types.id', ondelete='CASCADE'), primary_key=True)
)
