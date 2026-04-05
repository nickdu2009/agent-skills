ROLE_ORDER = {
    "viewer": 1,
    "editor": 2,
    "admin": 3,
}


def can_access_role(actual_role, required_role):
    return ROLE_ORDER[actual_role] >= ROLE_ORDER[required_role]
