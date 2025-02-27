from flask import Blueprint, request, jsonify

from app.decorators import validate_request, requires_user
from app.validators import validate_entity
from app.presenters import present_entity
from app.methods import create_entity, get_entities, get_entity, update_entity, delete_entity

entities_blueprint = Blueprint('entities', __name__)


@entities_blueprint.route('/', methods=['POST'])
@requires_user
@validate_request(validate_entity)
def create_entity_endpoint(entity_description):
    """Создание новой сущности."""
    entity = create_entity(entity_description)
    return present_entity(entity), 201


@entities_blueprint.route('/', methods=['GET'])
@requires_user
def get_entities_endpoint(user):
    """Получение всех сущностей."""
    entities = get_entities()
    return jsonify([present_entity(entity) for entity in entities]), 200


@entities_blueprint.route('/<int:entity_id>', methods=['GET'])
@requires_user
def get_entity_endpoint(user, entity_id):
    """Получение одной сущности по ID."""
    entity = get_entity(entity_id)
    return jsonify(present_entity(entity)), 200


@entities_blueprint.route('/<int:entity_id>', methods=['PUT'])
@requires_user
@validate_request(validate_entity)
def update_entity_endpoint(entity_description, user, entity_id):
    """Обновление сущности."""
    entity = get_entity(entity_id)
    update_entity(entity, entity_description)
    return present_entity(entity), 200


@entities_blueprint.route('/<int:entity_id>', methods=['DELETE'])
@requires_user
def delete_entity_endpoint(user, entity_id):
    """Удаление сущности."""
    entity = get_entity(entity_id)
    delete_entity(entity)
    return jsonify({'message': 'Запись удалена'}), 204
