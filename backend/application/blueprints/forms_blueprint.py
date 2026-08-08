from flask import Blueprint, jsonify
from application.helpers.decorators import *
from application.helpers.exceptions import LogicException
from application.validators import validate_form, validate_form_category
from application.presenters.presenters import *
from application.methods import *

forms_blueprint = Blueprint('forms', __name__, url_prefix='/forms')
submissions_blueprint = Blueprint('submissions', __name__, url_prefix='/submissions')


@forms_blueprint.route('', methods=['GET'])
@requires_user
def get_forms_endpoint(user):
    return jsonify([present_form(f) for f in get_forms() if can_get_form_category(user, f.category)]), 200


@forms_blueprint.route('/categories', methods=['GET'])
@requires_user
def get_form_categories_endpoint(user):
    return jsonify([present_form_category(fc) for fc in get_form_categories() if can_get_form_category(user, fc)]), 200


@forms_blueprint.route('/categories', methods=['POST'])
@requires_user
@requires_roles(['admin'])
@validate_request_with(validate_form_category)
def create_form_category_endpoint(validated_data, user):
    category = create_form_category(user, validated_data)
    return jsonify(present_form_category(category)), 201


@forms_blueprint.route('/categories/<int:category_id>', methods=['PUT'])
@requires_user
@requires_roles(['admin'])
@validate_request_with(validate_form_category)
def update_form_category_endpoint(validated_data, user, category_id):
    category = get_category_by_id(category_id)
    return jsonify(present_form_category(update_form_category(category, validated_data))), 200


@forms_blueprint.route('/categories/<int:category_id>', methods=['DELETE'])
@requires_user
@requires_roles(['admin'])
def delete_form_category_endpoint(user, category_id):
    category = get_category_by_id(category_id)
    delete_form_category(user, category)
    return jsonify({'deleted': True}), 200


@forms_blueprint.route('/categories/<int:category_id>/usage', methods=['GET'])
@requires_user
@requires_roles(['admin'])
def get_form_category_usage_endpoint(user, category_id):
    category = get_category_by_id(category_id)
    return jsonify(get_form_category_usage(category)), 200


@forms_blueprint.route('/categories/<int:category_id>', methods=['POST'])
@requires_user
@requires_roles(['admin'])
@validate_request_with(validate_form)
def create_form_endpoint(validated_data, user, category_id):
    category = get_category_by_id(category_id)
    new_form = create_form(user, category, validated_data)
    return jsonify(present_form(new_form)), 201


@forms_blueprint.route('/<int:form_id>', methods=['GET'])
@requires_user
def get_form_endpoint(user, form_id):
    form = get_form_by_id(form_id)
    if not can_get_form_category(user, form.category):
        raise LogicException("Доступ запрещен", 403)
    return jsonify(present_form(form)), 200


@forms_blueprint.route('/<int:form_id>/submissions', methods=['GET'])
@requires_user
@requires_roles(['admin'])
def get_form_submissions_endpoint(user, form_id):
    form = get_form_by_id(form_id)
    submissions = get_form_submissions(form)
    return jsonify(
        [present_submission(submission, present_object(submission.object, user)) for submission in submissions]), 200


@forms_blueprint.route('/<int:form_id>', methods=['PUT'])
@requires_user
@requires_roles(['admin'])
@validate_request_with(validate_form)
def update_form_endpoint(validated_data, user, form_id):
    form = get_form_by_id(form_id)
    updated = update_form(form, validated_data)
    return jsonify(present_form(updated)), 200


@forms_blueprint.route('/<int:form_id>', methods=['DELETE'])
@requires_user
@requires_roles(['admin'])
def delete_form_endpoint(user, form_id):
    form = get_form_by_id(form_id)
    delete_form(user, form)
    return jsonify({'deleted': True}), 200
