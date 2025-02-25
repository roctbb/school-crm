from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.group import Group
from app.models.entity import Entity
from app.models.user import User


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class EntitySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GroupSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Group
        include_fk = True
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    type = fields.Str(required=True, validate=validate.Length(min=1))
    participants = fields.Nested(EntitySchema, many=True, dump_only=True)
    owner = fields.Nested(UserSchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
