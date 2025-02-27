from app import LogicException
from app.decorators import transaction
from app.models.entity import Entity
from app.database import db
from app.validators import validate_entity


@transaction
def create_entity(data):
    """Создание новой сущности"""
    entity = Entity(
        name=data['name'],
        type_id=data['type_id'],
        owner_id=data.get('owner_id'),
        invite_code=data.get('invite_code')
    )
    db.session.add(entity)
    return entity


def get_entities():
    """Получить список всех сущностей"""
    return Entity.query.all()


def get_entity(entity_id):
    """Получить одну сущность по ID"""
    entity = Entity.query.get(entity_id)
    if not entity:
        raise LogicException('Entity not found', 404)
    return entity


@transaction
def update_entity(entity, data):
    """Обновить сущность"""
    entity.name = data['name']
    entity.type_id = data['type_id']
    entity.invite_code = data['invite_code']

    return entity


@transaction
def delete_entity(entity_id):
    """Удалить сущность"""
    entity = Entity.query.get(entity_id)
    if not entity:
        raise LogicException('Entity not found', 404)

    db.session.delete(entity)
