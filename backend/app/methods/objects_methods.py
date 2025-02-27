from app import ObjectType


def get_objects_types():
    return ObjectType.query.all()