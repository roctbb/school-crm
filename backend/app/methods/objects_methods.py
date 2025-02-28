from app.models import ObjectType, Object, db
from app.helpers.exceptions import LogicException
from app.helpers.decorators import transaction


def get_objects_types():
    return ObjectType.query.all()


def get_object_type_by_code(type_code):
    return ObjectType.query.filter_by(code=type_code).first()


def get_objects_by_type_code(type_code):
    object_type = get_object_type_by_code(type_code)

    if not object_type:
        raise LogicException("Неверный тип объекта", 404)

    # Получить объекты с указанным type_id
    return Object.query.filter_by(type_id=object_type.id).all()


@transaction
def create_object(user, type, data):
    new_object = Object(
        name=data["name"],
        type_id=type.id,
        attributes=data.get("attributes", {}),
        params=data.get("params", {}),
        creator_id=user.id,
    )
    db.session.add(new_object)
