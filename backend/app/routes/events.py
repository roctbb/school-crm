from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.event import Event
from app.database import db
from app.schemas.event import EventSchema

events_blueprint = Blueprint('events', __name__)

event_schema = EventSchema()
events_schema = EventSchema(many=True)


# GET /events - Получить список событий
@events_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_events():
    events = Event.query.all()
    return jsonify(events_schema.dump(events))


# POST /events - Создать новое событие
@events_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_event():
    data = request.json
    event = event_schema.load(data, session=db.session)
    db.session.add(event)
    db.session.commit()
    return event_schema.dump(event), 201


# GET /events/<id> - Получить информацию о конкретном событии
@events_blueprint.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return event_schema.dump(event)


# PUT /events/<id> - Обновить информацию о событии
@events_blueprint.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.json
    event = event_schema.load(data, instance=event, session=db.session)
    db.session.commit()
    return event_schema.dump(event)


# DELETE /events/<id> - Удалить событие
@events_blueprint.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Событие успешно удалено"}), 200
