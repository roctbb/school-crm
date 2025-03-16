from app import LogicException


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

    if user in object.owners and not object.is_approved:
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
    if has_admin_access(user):
        return True

    if user.role not in object_type.params.get('hidden_from', []):
        return True

    return False


def can_get_object(user, object):
    if has_admin_access(user):
        return True

    if can_get_object_type(user, object.type):
        return True

    return False

def can_get_form_category(user, form_category):
    if has_admin_access(user):
        return True

    if user.role not in form_category.params.get('hidden_from', []):
        return True

    return False

def can_get_submission(user, submission):
    if has_admin_access(user):
        return True

    if not submission.form or can_get_form_category(user, submission.form.category):
        return True

    return False