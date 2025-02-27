from app import LogicException


def should_have(data, param, min_length=None, max_length=None, required=True):
    value = data.get(param)

    if not value and required:
        raise LogicException(f"Отсутствует поле {param}", 400)

    if value is not None:
        if min_length is not None and len(value) < min_length:
            raise LogicException(f"Поле {param} короче {min_length}", 400)

        if max_length is not None and len(value) > max_length:
            raise LogicException(f"Поле {param} длинее {min_length}", 400)

def should_exist(data, param, model, target_param=None):
    value = data.get(param)

    if not target_param:
        target_param = param

    if not model.query.filter_by(**{target_param: value}).count():
        raise LogicException(f"Значение {value} для поля {param} не найдено.")

def should_be_unique(data, param, model):
    value = data.get(param)

    if model.query.filter_by(**{param: value}).count():
        raise LogicException(f"Значение {value} поля {param} уже используется", 400)
