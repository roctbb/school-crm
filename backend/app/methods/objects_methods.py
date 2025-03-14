import logging

from sqlalchemy.orm import subqueryload, selectinload

from app import Comment
from app.models import ObjectType, Object, db
from app.helpers.exceptions import LogicException
from app.helpers.decorators import transaction


def get_object_by_id(object_id):
    obj = Object.query.filter_by(id=object_id, deleted_at=None).first()

    if not obj:
        raise LogicException("Объект не найден", 404)

    return obj


def get_comment_by_id(comment_id):
    comment = Comment.query.filter_by(id=comment_id, deleted_at=None).first()

    if not comment:
        raise LogicException("Комментарий не найден", 404)

    return comment


def get_objects_types():
    return ObjectType.query.all()


def get_object_type_by_code(type_code):
    object_type = ObjectType.query.filter_by(code=type_code).first()

    if not object_type:
        raise LogicException("Категория не найдена", 404)

    return object_type


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_available_objects_by_type_code(type_code):
    object_type = get_object_type_by_code(type_code)

    logging.log(
        logging.INFO, "Begin query!!!")
    result = Object.query.filter_by(type_id=object_type.id, deleted_at=None).options(selectinload(Object.parents),
                                                                                     selectinload(Object.children),
                                                                                     selectinload(Object.owners),
                                                                                     selectinload(
                                                                                         Object.comments)).all()
    logging.log(
        logging.INFO, "End query!!!")
    return result


def get_available_objects():
    logging.log(
        logging.INFO, "Begin query!!!")
    result = Object.query.filter_by(deleted_at=None).options(selectinload(Object.parents),
                                                                                     selectinload(Object.children),
                                                                                     selectinload(Object.owners),
                                                                                     selectinload(
                                                                                         Object.comments)).all()
    logging.log(
        logging.INFO, "End query!!!")

    return result


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
    return new_object


@transaction
def delete_object(user, obj):
    obj.deleted_at = db.func.now()
    obj.deleter_id = user.id


@transaction
def update_object(obj, data):
    obj.name = data.get("name", obj.name)
    obj.attributes = data.get("attributes", obj.attributes)
    obj.params = data.get("params", obj.params)

    return obj


@transaction
def update_object_children(obj, children_ids):
    children = Object.query.filter(
        Object.id.in_(children_ids),
        Object.deleted_at == None
    ).all()

    if len(children) != len(children_ids):
        raise LogicException("Некоторые объекты из списка children не найдены или удалены.", 422)

    obj.children = children
    return obj


@transaction
def create_comment(user, object, validated_data):
    comment = Comment(creator_id=user.id, text=validated_data["text"], object_id=object.id)
    db.session.add(comment)

    return comment


@transaction
def delete_comment(user, obj):
    obj.deleted_at = db.func.now()
    obj.deleter_id = user.id
