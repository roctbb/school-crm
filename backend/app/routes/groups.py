from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.group import Group
from app.database import db
from app.schemas.group import GroupSchema

groups_blueprint = Blueprint('groups', __name__)

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)


# GET /groups - Получить список групп
@groups_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_groups():
    groups = Group.query.all()
    return jsonify(groups_schema.dump(groups))


# POST /groups - Создать новую группу
@groups_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_group():
    data = request.json
    group = group_schema.load(data, session=db.session)
    db.session.add(group)
    db.session.commit()
    return group_schema.dump(group), 201


# GET /groups/<id> - Получить информацию о конкретной группе
@groups_blueprint.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    group = Group.query.get_or_404(group_id)
    return group_schema.dump(group)


# PUT /groups/<id> - Обновить информацию группы
@groups_blueprint.route('/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    group = Group.query.get_or_404(group_id)
    data = request.json
    group = group_schema.load(data, instance=group, session=db.session)
    db.session.commit()
    return group_schema.dump(group)


# DELETE /groups/<id> - Удалить группу
@groups_blueprint.route('/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({"message": "Группа успешно удалена"}), 200
