import csv
from flask import current_app

from application import LogicException, Form
from application.helpers.decorators import transaction
from application.methods import create_submission
from application.models import Object, ObjectType, db


@transaction
def import_objects(user, file):
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


@transaction
def import_submissions(user, file):
    import csv
    from flask import current_app
    from application import LogicException
    from application.models import Object, Form
    # функция для создания Submission (аналог createSubmission)

    data = csv.DictReader(file.stream.read().decode('utf-8').splitlines())

    # Обязательные колонки
    required_columns = {'name', 'form'}
    if not set(required_columns).issubset(data.fieldnames):
        raise LogicException(
            f"Отсутствуют обязательные колонки: {', '.join(required_columns)}",
            400
        )

    imported_submissions = []

    for row in data:
        object_name = row.get('name')
        form_name = row.get('form')

        if not object_name or not form_name:
            current_app.logger.warning(
                f"Пропущена строка: нет нужных значений в name или form. {row}"
            )
            continue

        obj = (
            Object.query
            .filter(Object.deleted_at.is_(None))
            .filter(Object.name.ilike(f"%{object_name}%"))
            .first()
        )
        if not obj:
            current_app.logger.warning(
                f"Не найден объект для '{object_name}', пропуск строки."
            )
            continue

        form = Form.query.filter_by(name=form_name, deleted_at=None).first()
        if not form:
            current_app.logger.warning(
                f"Не найдена форма '{form_name}', пропуск строки."
            )
            continue

        common_fields = form.category.common_fields or []
        original_fields = form.fields or []

        fields = common_fields + original_fields

        # Собираем поля Submission: заполняем answers из CSV
        filled_fields = []
        for field_info in fields:
            field_name = field_info.get("name")
            if not field_name:
                continue

            csv_value = row.get(field_name, "").strip()

            filled_fields.append({
                "name": field_info.get("name"),
                "type": field_info.get("type"),
                "required": field_info.get("required", False),
                "options": field_info.get("options", []),
                "showoff": field_info.get("showoff", False),  # Если в форме есть такое поле
                "answer": csv_value
            })

        # Заполняем showoff_attributes
        showoff_attributes = {}
        for f in filled_fields:
            if f.get("showoff") and f.get("answer"):
                showoff_attributes[f["name"]] = f["answer"]

        submission_data = {
            "fields": filled_fields,
            "showoff_attributes": showoff_attributes,
        }

        new_submission = create_submission(user, form, obj, submission_data)
        imported_submissions.append(new_submission)

    current_app.logger.info(f"Импортировано ответов: {len(imported_submissions)}")
    return "OK"


