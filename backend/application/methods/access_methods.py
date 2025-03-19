from application import LogicException


def has_admin_access(user):
    return user.role == 'admin'


def has_teacher_access(user):
    return user.role == 'teacher' or has_admin_access(user)


def can_create_by_type(user, category):
    if has_teacher_access(user):
        return True

    if user.role in category.params.get('can_create', []):
        return True

    raise LogicException("Доступ запрещен", 403)


def can_fill_in_category(user, object_type):
    if has_teacher_access(user):
        return True

    if user.role in object_type.params.get('can_fill', []):
        return True

    raise LogicException("Доступ запрещен", 403)


def can_modify_object(user, object):
    if has_teacher_access(user):
        return True

    if user in object.owners:
        return True

    raise LogicException("Доступ запрещен", 403)


def can_delete_object(user, object):
    if has_teacher_access(user):
        return True

    if user in object.owners and not object.is_approved and user.role in object.params.get('can_delete', []):
        return True

    raise LogicException("Доступ запрещен", 403)


def can_comment_object(user, object):
    if has_teacher_access(user):
        return True

    if user.role in object.type.params.get('can_fill', []):
        return True

    raise LogicException("Доступ запрещен", 403)


def can_delete_comment(user, comment):
    if has_teacher_access(user):
        return True

    if user.id == comment.creator_id:
        return True

    raise LogicException("Доступ запрещен", 403)


def can_modify_submission(user, submission):
    if has_teacher_access(user):
        return True

    if user.id == submission.creator_id and not submission.is_approved:
        return True

    raise LogicException("Доступ запрещен", 403)


def can_get_object_type(user, object_type):
    if has_teacher_access(user):
        return True

    if not object_type.params.get('is_hidden', []):
        return True

    return False


def can_get_object(user, object):
    if has_admin_access(user):
        return True

    if can_get_object_type(user, object.type):
        return True

    return False


def can_get_form_category(user, form_category):
    if has_teacher_access(user):
        return True

    if not form_category.params.get('is_hidden'):
        return True

    return False


def can_get_submission(user, object, submission):
    if has_teacher_access(user):
        return True

    if submission.form.category.params.get('is_private') and user not in object.owners:
        return False

    if not submission.form or can_get_form_category(user, submission.form.category):
        return True

    return False


def filter_object_description_for_update(user, object, new_values):
    if has_teacher_access(user):
        return new_values

    new_attributes = new_values.get('attributes')

    if new_attributes:
        for attribute in object.type.available_attributes:
            if (attribute.get('is_hidden') or attribute.get('is_locked')) and new_attributes.get(attribute.get('code')):
                del new_attributes[attribute.get('code')]

                if object.attributes.get(attribute.get('code')):
                    new_attributes[attribute.get('code')] = object.attributes[attribute.get('code')]
    else:
        new_attributes = object.attributes

    new_values['attributes'] = new_attributes
    new_values['params'] = object.params

    return new_values