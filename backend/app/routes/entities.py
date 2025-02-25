from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.entity import Entity, EntityType
from app.database import db
from app.schemas.entity import EntitySchema, EntityTypeSchema

entities_blueprint = Blueprint('entities', __name__)

entity_schema = EntitySchema()
entities_schema = EntitySchema(many=True)
entity_type_schema = EntityTypeSchema()
entity_types_schema = EntityTypeSchema(many=True)


# GET /entities - Получить список сущностей
@entities_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_entities():
    return jsonify(entities_schema.dump(entities))


# POST /entities - Создать новую сущность
@entities_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_entity():
    data = request.json
    entity = entity_schema.load(data)
    db.session.add(entity)
    db.session.commit()
    return entity_schema.dump(entity), 201
