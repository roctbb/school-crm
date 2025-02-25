from marshmallow import Schema, fields, validates, validate, ValidationError
from app.models.user import User



# Схема для регистрации пользователя
class SignupSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=256))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    invite_code = fields.Str(required=False, validate=validate.Length(max=50))

    @validates('email')
    def validate_email(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError('Пользователь с таким email уже существует.')


# Схема для входа пользователя
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


# Схема для возвращаемого пользователя (например, для /auth/me)
class UserResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
