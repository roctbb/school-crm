from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.user import User, Role
from app.database import db
from app.schemas.user import UserSchema, RoleSchema

users_blueprint = Blueprint('users', __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)


# GET /users - Получить список пользователей (только авторизованные)
@users_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))


# POST /users - Создать нового пользователя (пример внутреннего использования)
@users_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_user():
    data = request.json
    user = user_schema.load(data)
    db.session.add(user)
    db.session.commit()
    return user_schema.dump(user), 201


# GET /roles - Получить список ролей
@users_blueprint.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    roles = Role.query.all()
    return jsonify(roles_schema.dump(roles))
