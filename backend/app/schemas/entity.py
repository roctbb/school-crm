from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.entity import Entity, EntityType


class EntityTypeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EntityType
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))


class EntitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Entity
        include_fk = True
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    type = fields.Nested(EntityTypeSchema, dump_only=True)
    parents = fields.Nested(lambda: EntitySchema(), many=True, dump_only=True)
    children = fields.Nested(lambda: EntitySchema(), many=True, dump_only=True)

