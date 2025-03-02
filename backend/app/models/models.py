from .tables import *
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())

    objects = db.relationship('Object', secondary=users_objects, back_populates='owners')


class ObjectType(db.Model):
    __tablename__ = 'object_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), nullable=False)

    available_attributes = db.Column(db.JSON, server_default=db.text("'[]'::json"))
    available_params = db.Column(db.JSON, server_default=db.text("'[]'::json"))

    params = db.Column(db.JSON, server_default=db.text("'{}'::json"))

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    form_categories = db.relationship(
        'FormCategory',
        secondary=object_types_form_categories,
        back_populates='object_types'
    )


class Object(db.Model):
    __tablename__ = 'objects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    params = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    attributes = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # foreign keys
    type_id = db.Column(db.Integer, db.ForeignKey('object_types.id', ondelete='CASCADE'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # relations
    parents = db.relationship(
        'Object',
        secondary='objects_children',
        primaryjoin=id == objects_children.c.child_id,
        secondaryjoin=id == objects_children.c.parent_id,
        backref=db.backref('children', lazy='dynamic'),
        lazy='dynamic'
    )

    type = db.relationship('ObjectType')
    owners = db.relationship('User', secondary=users_objects, back_populates='objects')

    # Исправленное отношение с Submission
    submissions = db.relationship('Submission', back_populates='object')
    comments = db.relationship('Comment', backref='object')

    created_by = db.relationship('User', foreign_keys=[creator_id])
    deleted_by = db.relationship('User', foreign_keys=[deleter_id])


class FormCategory(db.Model):
    __tablename__ = 'form_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=True)
    params = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    forms = db.relationship('Form', backref='category')

    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('form_categories.id', ondelete='CASCADE'), nullable=True)

    # relations
    created_by = db.relationship('User', foreign_keys=[creator_id])
    deleted_by = db.relationship('User', foreign_keys=[deleter_id])

    object_types = db.relationship(
        'ObjectType',
        secondary=object_types_form_categories,
        back_populates='form_categories'
    )


class Form(db.Model):
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    available_params = db.Column(db.JSON, server_default=db.text("'[]'::json"))
    fields = db.Column(db.JSON, server_default=db.text("'[]'::json"))
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('form_categories.id', ondelete='CASCADE'), nullable=False)

    # relations
    created_by = db.relationship('User', foreign_keys=[creator_id])
    deleted_by = db.relationship('User', foreign_keys=[deleter_id])
    submissions = db.relationship('Submission', back_populates='form')


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)

    params = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    answers = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # keys
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id', ondelete="CASCADE"), nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey('objects.id', ondelete="CASCADE"), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # relations
    form = db.relationship('Form', back_populates='submissions')
    object = db.relationship('Object', back_populates='submissions')  # Связывает с Object
    created_by = db.relationship('User', foreign_keys=[creator_id])
    deleted_by = db.relationship('User', foreign_keys=[deleter_id])


class Invitation(db.Model):
    __tablename__ = 'invitations'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=True)
    key = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(100), nullable=False)

    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)

    # keys
    object_id = db.Column(db.Integer, db.ForeignKey('objects.id', ondelete="CASCADE"), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=True)

    created_by = db.relationship('User', foreign_keys=[creator_id])
    deleted_by = db.relationship('User', foreign_keys=[deleter_id])
    used_by = db.relationship('User', foreign_keys=[user_id])
    object = db.relationship('Object')


class UploadedFile(db.Model):
    __tablename__ = "uploaded_files"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=True)

    # Определяем отношение к модели User
    user = db.relationship("User", backref="uploaded_files")


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="comments")
