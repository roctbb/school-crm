from .presenters import present_entity


def present_role(role):
    return role.name


def present_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "roles": [present_role(role) for role in user.roles],
        "entities": [present_entity(entity) for entity in user.entities]
    }
