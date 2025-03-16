from flask import Blueprint, jsonify
from app.helpers.decorators import requires_user, validate_request_with, requires_roles
from app.validators import validate_form
from app.presenters.presenters import present_form, present_form_category
from app.methods import (
    get_form_by_id, get_forms, get_form_categories, create_form, update_form, delete_form,
    get_category_by_id, can_get_form_category
)

forms_blueprint = Blueprint('forms', __name__, url_prefix='/forms')
submissions_blueprint = Blueprint('submissions', __name__, url_prefix='/submissions')


@forms_blueprint.route('', methods=['GET'])
@requires_user
def get_forms_endpoint(user):
    return jsonify([present_form(f) for f in get_forms()]), 200

@forms_blueprint.route('/categories', methods=['GET'])
@requires_user
def get_form_categories_endpoint(user):
    return jsonify([present_form_category(fc) for fc in get_form_categories() if can_get_form_category(user, fc)]), 200


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
    return jsonify(present_form(form)), 200


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