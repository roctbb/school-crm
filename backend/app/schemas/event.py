from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.event import Event
from app.models.group import Group


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        include_fk = True
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    group = fields.Nested(GroupSchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
