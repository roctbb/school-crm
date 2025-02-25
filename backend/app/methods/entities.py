from app.models.entity import Entity
from app.database import db


def get_all_entities():
    """Получить все сущности."""
    return Entity.query.all()


def create_new_entity(data):
    """Создать новую сущность."""
    entity = Entity(**data)
    db.session.add(entity)
    db.session.commit()
    return entity
