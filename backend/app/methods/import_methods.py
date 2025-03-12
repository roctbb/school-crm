import csv
from flask import current_app

from app import LogicException
from app.helpers.decorators import transaction
from app.models import Object, ObjectType, db


@transaction
def import_data(user, file):
    # Открываем файл через TextIOWrapper для корректного чтения
    data = csv.DictReader(file.stream.read().decode('utf-8').splitlines())

    # Проверяем обязательные колонки
    required_columns = {'name', 'type'}
    if not set(required_columns).issubset(set(data.fieldnames)):
        raise LogicException(f"Отсутствуют обязательные колонки: {', '.join(required_columns)}", 400)

    imported_objects = []

    for row in data:
        # Извлекаем обязательные поля
        name = row.get('name')
        type_code = row.get('type')

        if not name or not type_code:
            current_app.logger.warning(f"Пропущена строка: name или type отсутствует. {row}")
            continue

        # Проверяем, существует ли ObjectType для заданного type_code
        object_type = ObjectType.query.filter_by(code=type_code).first()
        if not object_type:
            current_app.logger.warning(f"Пропуск строки: не удалось найти ObjectType с кодом {type_code}")
            continue

        # Фильтруем колонки, относящиеся к attributes
        attributes = {}
        for key, value in row.items():
            value = value.strip() if value else None
            if key.startswith('attributes_'):
                attr_key = key.replace('attributes_', '', 1)
                if value:
                    if attr_key not in attributes:
                        attributes[attr_key] = [] if value else []
                    attributes[attr_key].append(value)

        # Фильтруем колонки, относящиеся к params
        params = {key.replace('params_', '', 1): value for key, value in row.items() if key.startswith('params_')}

        for attribute in attributes:
            if len(attributes[attribute]) == 1:
                attributes[attribute] = attributes[attribute][0]

        existing_object = Object.query.filter_by(name=name, type_id=object_type.id).first()

        if existing_object:
            for key in attributes:
                existing_object.attributes[key] = attributes[key]

            for key in params:
                existing_object.params[key] = params[key]

        else:
            new_object = Object(
                name=name,
                type_id=object_type.id,
                attributes=attributes,
                params=params,
                creator_id=user.id
            )
            db.session.add(new_object)
            imported_objects.append(new_object)

    current_app.logger.info(f"Импортировано объектов: {len(imported_objects)}")
    return "OK"
