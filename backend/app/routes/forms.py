from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.form import Form, FormCategory
from app.database import db
from app.schemas.form import FormSchema, FormCategorySchema

forms_blueprint = Blueprint('forms', __name__)

form_schema = FormSchema()
forms_schema = FormSchema(many=True)


# GET /forms - Получить список форм (авторизация требуется)
@forms_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_forms():
    forms = Form.query.all()
    return jsonify(forms_schema.dump(forms))


# POST /forms - Создать новую форму
@forms_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_form():
    data = request.json
    form = form_schema.load(data)
    db.session.add(form)
    db.session.commit()
    return form_schema.dump(form), 201
