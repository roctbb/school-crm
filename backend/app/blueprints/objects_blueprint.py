from flask import Blueprint, jsonify

from app.helpers.decorators import requires_user, validate_request_with, requires_roles
from app.methods import *
from app.presenters import *
from app.validators import validate_object, validate_object_children, validate_comment, validate_submission

objects_blueprint = Blueprint('objects', __name__, url_prefix='/objects')


@objects_blueprint.route('/types', methods=['GET'])
@requires_user
def object_types(user):
    return jsonify([present_object_type(object_type, user) for object_type in get_objects_types() if
                    can_get_object_type(user, object_type)])


@objects_blueprint.route('/<string:type_code>', methods=['GET'])
@requires_user
def object_type_endpoint(user, type_code):
    objects = get_available_objects_by_type_code(type_code)
    return jsonify([present_object(obj, user) for obj in objects if can_get_object(user, obj)]), 200


@objects_blueprint.route('', methods=['GET'])
@requires_user
def objects_endpoint(user):
    objects = get_available_objects()
    return jsonify([present_object(obj, user) for obj in objects if can_get_object(user, obj)]), 200


@objects_blueprint.route('/<string:type_code>/create', methods=['POST'])
@requires_user
@validate_request_with(validate_object)
def create_object_endpoint(validated_data, user, type_code):
    object_type = get_object_type_by_code(type_code)

    if can_create_by_type(user, object_type):
        return jsonify(present_object(create_object(user, object_type, validated_data), user)), 201


@objects_blueprint.route('/<int:object_id>/approve', methods=['POST'])
@requires_user
@requires_roles(['admin', 'teacher'])
def approve_object_endpoint(user, object_id, ):
    obj = get_object_by_id(object_id)
    return jsonify(present_object(approve_object(user, obj), user)), 200


@objects_blueprint.route('/<int:object_id>', methods=['PUT'])
@requires_user
@validate_request_with(validate_object)
def update_object_endpoint(validated_data, user, object_id):
    obj = get_object_by_id(object_id)
    if can_modify_object(user, obj):
        if not has_teacher_access(user):
            deapprove_object(obj)

        validated_data = filter_object_description_for_update(user, obj, validated_data)
        return jsonify(present_object(update_object(user, obj, validated_data), user)), 200


@objects_blueprint.route('/<int:object_id>', methods=['DELETE'])
@requires_user
def delete_object_endpoint(user, object_id):
    obj = get_object_by_id(object_id)

    if can_delete_object(user, obj):
        delete_object(user, obj)
        return jsonify({'deteted': True}), 200


@objects_blueprint.route('/<int:object_id>/children', methods=['PUT'])
@requires_user
@validate_request_with(validate_object_children)
def update_object_children_endpoint(validated_data, user, object_id):
    obj = get_object_by_id(object_id)
    children_ids = validated_data.get('children', [])
    if can_modify_object(user, obj):
        updated_object = update_object_children(user, obj, children_ids)
        return jsonify([present_connected_object(child) for child in updated_object.children]), 200


@objects_blueprint.route('/<int:object_id>/comments', methods=['POST'])
@requires_user
@validate_request_with(validate_comment)
def add_comment(validated_data, user, object_id):
    object = get_object_by_id(object_id)

    if can_comment_object(user, object):
        return jsonify(present_comment(create_comment(user, object, validated_data))), 201


@objects_blueprint.route('/<int:object_id>/comments/<int:comment_id>', methods=['DELETE'])
@requires_user
def delete_comment_endpoint(user, object_id, comment_id):
    object = get_object_by_id(object_id)
    comment = get_comment_by_id(comment_id)

    if can_delete_comment(user, comment):
        delete_comment(user, comment)
        return jsonify({'deteted': True}), 200


@objects_blueprint.route('/<int:object_id>/forms/<int:form_id>', methods=['POST'])
@requires_user
@validate_request_with(validate_submission)
def create_submission_endpoint(validated_data, user, object_id, form_id):
    object = get_object_by_id(object_id)
    form = get_form_by_id(form_id)
    if can_fill_in_category(user, form.category) and can_modify_object(user, object):
        new_sub = create_submission(user, form, object, validated_data)
        return jsonify(present_submission(new_sub)), 201


@objects_blueprint.route('/<int:object_id>/submissions', methods=['GET'])
@requires_user
def get_submissions_endpoint(user, object_id):
    object = get_object_by_id(object_id)
    return [present_submission(submission) for submission in get_object_submissions(object) if
            can_get_submission(user, object, submission)], 200


@objects_blueprint.route('/<int:object_id>/submissions/<int:submission_id>', methods=['PUT'])
@requires_user
@validate_request_with(validate_submission)
def update_submission_endpoint(validated_data, user, object_id, submission_id):
    sub = get_submission_by_id(submission_id)

    if can_modify_submission(user, sub):
        updated = update_submission(sub, validated_data)
        return jsonify(present_submission(updated)), 200


@objects_blueprint.route('/<int:object_id>/submissions/<int:submission_id>/approve', methods=['POST'])
@requires_user
@requires_roles(['admin', 'teacher'])
def approve_submission_endpoint(user, object_id, submission_id):
    sub = get_submission_by_id(submission_id)
    return jsonify(present_submission(approve_submission(user, sub))), 200


@objects_blueprint.route('/<int:object_id>/submissions/<int:submission_id>', methods=['DELETE'])
@requires_user
def delete_submission_endpoint(user, object_id, submission_id):
    sub = get_submission_by_id(submission_id)

    if can_modify_submission(user, sub):
        delete_submission(user, sub)
        return jsonify({'deleted': True}), 200
