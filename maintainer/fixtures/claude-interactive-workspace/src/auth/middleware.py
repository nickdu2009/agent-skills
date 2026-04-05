from src.auth.role_check import can_access_role
from src.auth.session_store import SessionStore


class AuthMiddleware:
    def __init__(self, session_store=None):
        self.session_store = session_store or SessionStore()

    def authorize(self, token, required_role):
        session = self.session_store.load(token)
        if session is None:
            return False
        return can_access_role(session["role"], required_role)
