from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.comment import Comment
from app.models.entity import Entity
from app.models.user import User


class EntitySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        include_fk = True
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    text = fields.Str(required=True, validate=validate.Length(min=1))
    entity = fields.Nested(EntitySchema, dump_only=True)
    author = fields.Nested(UserSchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
