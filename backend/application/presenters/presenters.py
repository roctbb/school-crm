import logging

from application.methods import can_get_form_category, has_admin_access, has_teacher_access


def present_user(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }


def present_object_type(object_type, user):
    return {
        'id': object_type.id,
        'name': object_type.name,
        'code': object_type.code,
        'form_categories': [present_related_form_category(category) for category in object_type.form_categories if
                            not category.deleted_at and can_get_form_category(user, category)],
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


def present_object(obj, user=None):
    def filter_attributes(attributes):
        if not user or has_admin_access(user):
            return attributes

        for attribute in obj.type.available_attributes:
            if attribute.get('code') in attributes:
                if attribute.get('is_private') and user not in obj.owners:
                    del attributes[attribute.get('code')]

                elif attribute.get('is_hidden'):
                    del attributes[attribute.get('code')]

        return attributes

    invitation = None
    has_registered_owner = bool([invitation for invitation in obj.invitations if
                                 invitation.used_at])

    if user and has_admin_access(user):
        invitations = [invitation for invitation in obj.invitations if
                       not invitation.used_at and not invitation.deleted_at]

        if invitations:
            invitation = present_invitation(invitations[0])

    comments = []

    if (user and has_teacher_access(user)) or not obj.type.params.get('comments_hidden'):
        comments = [present_comment(comment) for comment in obj.comments if not comment.deleted_at]

    return {
        'id': obj.id,
        'name': obj.name,
        'params': obj.params,
        'attributes': filter_attributes(obj.attributes),
        'type': obj.type.code,
        'is_approved': obj.is_approved,
        'has_unapproved_submissions': obj.has_unapproved_submissions,
        'creator': present_user(obj.created_by) if obj.created_by else None,
        'deleter': present_user(obj.deleted_by) if obj.deleted_by else None,
        'created_at': obj.created_at.isoformat(),
        'updated_at': obj.updated_at.isoformat(),
        'deleted_at': obj.deleted_at.isoformat() if obj.deleted_at else None,
        'owners': [present_user(owner) for owner in obj.owners],
        'children': [present_connected_object(child) for child in obj.children if not child.deleted_at],
        'parents': [present_connected_object(child) for child in obj.parents if not child.deleted_at],
        'comments': comments,
        'invitation': invitation,
        'has_registered_owner': has_registered_owner
    }


def present_comment(comment):
    return {
        'id': comment.id,
        'text': comment.text,
        'author': present_user(comment.created_by),
        'created_at': comment.created_at.isoformat(),
    }


def present_form_category(form_category):
    return {
        'id': form_category.id,
        'name': form_category.name,
        'params': form_category.params,
        'forms': [present_form(form) for form in form_category.forms if not form.deleted_at],
        'common_fields': form_category.common_fields
    }


def present_related_form_category(form_category):
    return {
        'id': form_category.id,
        'params': form_category.params,
        'name': form_category.name
    }


def present_form(form):
    return {
        'id': form.id,
        'name': form.name,
        'category_id': form.category_id,
        'available_params': form.available_params,
        'fields': form.fields,
        'creator': present_user(form.created_by) if form.created_by else None,
        'deleter': present_user(form.deleted_by) if form.deleted_by else None,
        'created_at': form.created_at.isoformat(),
        'updated_at': form.updated_at.isoformat(),
        'deleted_at': form.deleted_at.isoformat() if form.deleted_at else None
    }


def present_submission(submission, object=None):
    return {
        'id': submission.id,
        'params': submission.params,
        'fields': submission.fields,
        'showoff_attributes': submission.showoff_attributes,
        'is_approved': submission.is_approved,
        'form': {
            'name': submission.form_name,
            'category': submission.form_category_name,
            'is_external': submission.is_external,
            'id': submission.form_id
        },
        'creator': present_user(submission.created_by) if submission.created_by else None,
        'deleter': present_user(submission.deleted_by) if submission.deleted_by else None,
        'created_at': submission.created_at.isoformat(),
        'updated_at': submission.updated_at.isoformat(),
        'deleted_at': submission.deleted_at.isoformat() if submission.deleted_at else None,
        'object': object
    }


def present_related_form(form):
    return {
        'id': form.id,
        'name': form.name,
        'category': present_related_form_category(form.category)
    }


def present_invitation(invitation):
    return {
        'id': invitation.id,
        'email': invitation.email,
        'key': invitation.key,
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
