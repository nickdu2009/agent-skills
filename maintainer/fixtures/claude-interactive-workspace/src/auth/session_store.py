from config.timeouts import SESSION_LOOKUP_TIMEOUT_SECONDS


class SessionStore:
    def __init__(self):
        self.timeout_seconds = SESSION_LOOKUP_TIMEOUT_SECONDS
        self.sessions = {
            "token-admin": {"user_id": "u-1", "role": "admin"},
            "token-viewer": {"user_id": "u-2", "role": "viewer"},
        }

    def load(self, token):
        return self.sessions.get(token)
