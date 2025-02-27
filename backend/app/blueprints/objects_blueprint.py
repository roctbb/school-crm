from flask import Blueprint
from app.helpers.decorators import requires_user
from app.methods import get_objects_types
from app.presenters.presenters import present_object, present_object_type

objects_blueprint = Blueprint('objects', __name__, url_prefix='/objects')


@objects_blueprint.route('/', methods=['GET'])
@requires_user
def object_types(user):
    return [present_object_type(object_type) for object_type in get_objects_types()]
