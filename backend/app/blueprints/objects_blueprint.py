from flask import Blueprint, jsonify

from app import LogicException
from app.helpers.decorators import requires_user, validate_request_with
from app.methods import get_objects_types, get_object_type_by_code, get_objects_by_type_code
from app.presenters.presenters import present_object, present_object_type
from app.validators import validate_object

objects_blueprint = Blueprint('objects', __name__, url_prefix='/objects')


@objects_blueprint.route('/', methods=['GET'])
@requires_user
def object_types(user):
    return jsonify([present_object_type(object_type) for object_type in get_objects_types()])


@objects_blueprint.route('/<string:type_code>/', methods=['GET'])
@requires_user
def object_type_endpoint(user, type_code):
    objects = get_objects_by_type_code(type_code)
    return jsonify([present_object(obj) for obj in objects]), 200


@objects_blueprint.route('/<string:type_code>/create', methods=['POST'])
@requires_user
@validate_request_with(validate_object)
def create_object_endpoint(user, validated_data, type_code):
    object_type = get_object_type_by_code(type_code)

    if not object_type:
        raise LogicException("Неверный тип объекта", 404)

    return jsonify(present_object(create_object(user, object_type, validated_data))), 201
