from enum import StrEnum


class AuditAction(StrEnum):
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_LOGOUT_ALL = "auth.logout_all"

    USER_CREATED = "user.created"
    USER_DELETED = "user.deleted"

    SECURITY_SESSION_REVOKED = "security.session_revoked"
    SECURITY_TOKEN_THEFT = "security.token_theft"
    SECURITY_ALL_SESSIONS_REVOKED = "security.all_sessions_revoked"
