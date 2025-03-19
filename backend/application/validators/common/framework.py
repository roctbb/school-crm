from application import LogicException


def should_have(data, param, min_length=None, max_length=None, required=True, options=None):
    value = data.get(param)

    if not value and required:
        raise LogicException(f"Отсутствует поле {param}", 400, field=param)

    if value is not None:
        if min_length is not None and len(value) < min_length:
            raise LogicException(f"Поле {param} короче {min_length}", 400, field=param)

        if max_length is not None and len(value) > max_length:
            raise LogicException(f"Поле {param} длиннее {min_length}", 400, field=param)

    if options is not None and value not in options:
        raise LogicException(f"Поле {param} должны быть одним из {options}")


def should_exist(data, param, model, target_param=None):
    value = data.get(param)

    if not target_param:
        target_param = param

    if not model.query.filter_by(**{target_param: value}).count():
        raise LogicException(f"Значение {value} для поля {param} не найдено.", 400, field=param)


def should_be_unique(data, param, model):
    value = data.get(param)

    if model.query.filter_by(**{param: value}).count():
        raise LogicException(f"Значение {value} поля {param} уже используется", 400, field=param)
