def present_user(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }


def present_object_type(object_type):
    return {
        'id': object_type.id,
        'name': object_type.name,
        'code': object_type.code,
        'available_attributes': object_type.available_attributes,
        'available_params': object_type.available_params,
        'params': object_type.params,
        'created_at': object_type.created_at.isoformat(),
        'updated_at': object_type.updated_at.isoformat()
    }


def present_connected_object(obj):
    return {
        'id': obj.id,
        'name': obj.name,
        'type': obj.type.code
    }


def present_object(obj):
    return {
        'id': obj.id,
        'name': obj.name,
        'params': obj.params,
        'attributes': obj.attributes,
        'type': obj.type.code,
        'creator': present_user(obj.created_by) if obj.created_by else None,
        'deleter': present_user(obj.deleted_by) if obj.deleted_by else None,
        'created_at': obj.created_at.isoformat(),
        'updated_at': obj.updated_at.isoformat(),
        'deleted_at': obj.deleted_at.isoformat() if obj.deleted_at else None,
        'owners': [present_user(owner) for owner in obj.owners],
        'children': [present_connected_object(child) for child in obj.children],
        'parents': [present_connected_object(child) for child in obj.parents]
    }


def present_form(form):
    return {
        'id': form.id,
        'name': form.name,
        'available_params': form.available_params,
        'fields': form.fields,
        'creator': present_user(form.created_by) if form.created_by else None,
        'deleter': present_user(form.deleted_by) if form.deleted_by else None,
        'created_at': form.created_at.isoformat(),
        'updated_at': form.updated_at.isoformat(),
        'deleted_at': form.deleted_at.isoformat() if form.deleted_at else None
    }


def present_submission(submission):
    return {
        'id': submission.id,
        'params': submission.params,
        'answers': submission.answers,
        'form_id': submission.form_id,
        'object_id': submission.object_id,
        'creator': present_user(submission.created_by) if submission.created_by else None,
        'deleter': present_user(submission.deleted_by) if submission.deleted_by else None,
        'created_at': submission.created_at.isoformat(),
        'updated_at': submission.updated_at.isoformat(),
        'deleted_at': submission.deleted_at.isoformat() if submission.deleted_at else None
    }


def present_invitation(invitation):
    return {
        'id': invitation.id,
        'email': invitation.email,
        'role': invitation.role,
        'used_at': invitation.used_at.isoformat() if invitation.used_at else None,
        'created_at': invitation.created_at.isoformat(),
        'updated_at': invitation.updated_at.isoformat(),
        'deleted_at': invitation.deleted_at.isoformat() if invitation.deleted_at else None,
        'object_id': invitation.object_id,
        'creator': present_user(invitation.created_by) if invitation.created_by else None,
        'deleter': present_user(invitation.deleted_by) if invitation.deleted_by else None,
        'used_by': present_user(invitation.used_by) if invitation.used_by else None
    }
