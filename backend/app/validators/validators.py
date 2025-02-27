from flask import request
from app import LogicException
from app.validators.helpers import should_have, should_be_unique
from app.models import Comment, Entity, Event, Form, Group


# Валидаторы для модели Comment
def validate_comment(data):
    should_have(data, 'text', min_length=1, max_length=256)
    should_have(data, 'entity_id')
    return data


# Валидаторы для модели Entity
def validate_entity(data):
    should_have(data, 'name', min_length=1, max_length=256)
    should_have(data, 'type_id')
    should_be_unique(data, 'name', Entity)
    return data


# Валидаторы для модели Event
def validate_event(data):
    should_have(data, 'name', min_length=1, max_length=256)
    should_have(data, 'start_date')
    should_have(data, 'end_date')
    if data.get('start_date') >= data.get('end_date'):
        raise LogicException("Дата начала события должна быть раньше даты окончания", 400)
    return data


# Валидаторы для модели Form
def validate_form(data):
    should_have(data, 'name', min_length=1, max_length=50)
    should_have(data, 'questions')
    return data


# Валидаторы для модели Group
def validate_group(data):
    should_have(data, 'name', min_length=1, max_length=256)
    should_have(data, 'type', min_length=1, max_length=256)
    return data
