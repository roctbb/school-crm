# Презенторы для модели Comment
def present_comment(comment):
    return {
        "id": comment.id,
        "text": comment.text,
        "author_id": comment.author_id,
        "entity_id": comment.entity_id,
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat()
    }


def present_comments(comments):
    return [present_comment(comment) for comment in comments]


# Презенторы для модели Entity
def present_entity_type(entity_type):
    return entity_type.name


def present_entity(entity):
    return {
        "id": entity.id,
        "name": entity.name,
        "type": present_entity_type(entity.type),
        "owner_id": entity.owner_id,
        "invite_code": entity.invite_code
    }


# Презенторы для модели Event
def present_event(event):
    return {
        "id": event.id,
        "name": event.name,
        "start_date": event.start_date.isoformat(),
        "end_date": event.end_date.isoformat(),
        "group_id": event.group_id,
        "created_at": event.created_at.isoformat(),
        "updated_at": event.updated_at.isoformat()
    }


def present_events(events):
    return [present_event(event) for event in events]


# Презенторы для модели Form
def present_form(form):
    return {
        "id": form.id,
        "name": form.name,
        "questions": form.questions,
        "category_id": form.category_id,
        "visible_for_roles": [role.name for role in form.visible_for],
        "created_at": form.created_at.isoformat(),
        "updated_at": form.updated_at.isoformat()
    }


def present_forms(forms):
    return [present_form(form) for form in forms]


# Презенторы для модели Group
def present_group(group):
    return {
        "id": group.id,
        "name": group.name,
        "type": group.type,
        "icon": group.icon,
        "owner_id": group.owner_id,
        "participants": [participant.id for participant in group.participants],
        "created_at": group.created_at.isoformat(),
        "updated_at": group.updated_at.isoformat()
    }


def present_groups(groups):
    return [present_group(group) for group in groups]
