from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.form import Form, FormCategory, FormSubmission
from app.models.user import Role


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True


class FormCategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FormCategory
        include_fk = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))


class FormSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Form
        include_fk = True
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    questions = fields.Dict()  # JSON формат полей формы
    category = fields.Nested(FormCategorySchema, dump_only=True)
    visible_for = fields.Nested(RoleSchema, many=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class FormSubmissionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FormSubmission
        include_fk = True
        load_instance = True

    id = fields.Int(dump_only=True)
    form = fields.Nested(FormSchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
