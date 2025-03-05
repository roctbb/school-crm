from flask import Blueprint, jsonify

from app import LogicException
from app.helpers.decorators import requires_user, validate_request_with
from app.methods import get_objects_types, get_object_type_by_code, get_available_objects_by_type_code, create_object, \
    get_available_objects, get_object_by_id, update_object, delete_object, update_object_children, create_comment, \
    delete_comment, get_comment_by_id, create_submission, get_form_by_id, get_submission_by_id, update_submission, \
    delete_submission, get_object_submissions
from app.presenters.presenters import present_object, present_object_type, present_connected_object, present_comment, \
    present_submission
from app.validators import validate_object, validate_object_children, validate_comment, validate_submission

objects_blueprint = Blueprint('objects', __name__, url_prefix='/objects')


@objects_blueprint.route('/types', methods=['GET'])
@requires_user
def object_types(user):
    return jsonify([present_object_type(object_type) for object_type in get_objects_types()])


@objects_blueprint.route('/<string:type_code>', methods=['GET'])
@requires_user
def object_type_endpoint(user, type_code):
    objects = get_available_objects_by_type_code(type_code)
    return jsonify([present_object(obj) for obj in objects]), 200


@objects_blueprint.route('', methods=['GET'])
@requires_user
def objects_endpoint(user):
    objects = get_available_objects()
    return jsonify([present_object(obj) for obj in objects]), 200


@objects_blueprint.route('/<string:type_code>/create', methods=['POST'])
@requires_user
@validate_request_with(validate_object)
def create_object_endpoint(validated_data, user, type_code):
    object_type = get_object_type_by_code(type_code)
    return jsonify(present_object(create_object(user, object_type, validated_data))), 201


from flask import request


@objects_blueprint.route('/<int:object_id>', methods=['PUT'])
@requires_user
@validate_request_with(validate_object)
def update_object_endpoint(validated_data, user, object_id):
    obj = get_object_by_id(object_id)
    return jsonify(present_object(update_object(obj, validated_data))), 200


@objects_blueprint.route('/<int:object_id>', methods=['DELETE'])
@requires_user
def delete_object_endpoint(user, object_id):
    obj = get_object_by_id(object_id)
    delete_object(obj)
    return jsonify({'deteted': True}), 200


@objects_blueprint.route('/<int:object_id>/children', methods=['PUT'])
@requires_user
@validate_request_with(validate_object_children)
def update_object_children_endpoint(validated_data, user, object_id):
    obj = get_object_by_id(object_id)
    children_ids = validated_data.get('children', [])
    updated_object = update_object_children(obj, children_ids)
    return jsonify([present_connected_object(child) for child in updated_object.children]), 200


@objects_blueprint.route('/<int:object_id>/comments', methods=['POST'])
@requires_user
@validate_request_with(validate_comment)
def add_comment(validated_data, user, object_id):
    object = get_object_by_id(object_id)
    return jsonify(present_comment(create_comment(user, object, validated_data))), 201


@objects_blueprint.route('/<int:object_id>/comments/<int:comment_id>', methods=['DELETE'])
@requires_user
def delete_comment_endpoint(user, object_id, comment_id):
    object = get_object_by_id(object_id)
    comment = get_comment_by_id(comment_id)
    delete_comment(comment)
    return jsonify({'deteted': True}), 200


@objects_blueprint.route('/<int:object_id>/forms/<int:form_id>', methods=['POST'])
@requires_user
@validate_request_with(validate_submission)
def create_submission_endpoint(validated_data, user, object_id, form_id):
    object = get_object_by_id(object_id)
    form = get_form_by_id(form_id)
    new_sub = create_submission(user, form, object, validated_data)
    return jsonify(present_submission(new_sub)), 201


@objects_blueprint.route('/<int:object_id>/submissions', methods=['GET'])
@requires_user
def get_submissions_endpoint(user, object_id):
    object = get_object_by_id(object_id)
    return [present_submission(submission) for submission in get_object_submissions(object)], 200


@objects_blueprint.route('/<int:object_id>/submissions/<int:submission_id>', methods=['PUT'])
@requires_user
@validate_request_with(validate_submission)
def update_submission_endpoint(validated_data, user, object_id, submission_id):
    sub = get_submission_by_id(submission_id)
    updated = update_submission(sub, validated_data)
    return jsonify(present_submission(updated)), 200


@objects_blueprint.route('/<int:object_id>/submissions/<int:submission_id>', methods=['DELETE'])
@requires_user
def delete_submission_endpoint(user, submission_id):
    sub = get_submission_by_id(submission_id)
    delete_submission(sub)
    return jsonify({'deleted': True}), 200
