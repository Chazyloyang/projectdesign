"""Role-based access control definitions."""

from enum import Enum
from typing import Set


class Role(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    SECURITY_ANALYST = "security_analyst"
    MANAGER = "manager"


class Permission(str, Enum):
    MANAGE_ORGS = "manage_orgs"
    MANAGE_USERS = "manage_users"
    MANAGE_INTEGRATIONS = "manage_integrations"
    CONNECT_REPOS = "connect_repos"
    RUN_PIPELINES = "run_pipelines"
    VIEW_VULNERABILITIES = "view_vulnerabilities"
    SUPPRESS_VULNERABILITIES = "suppress_vulnerabilities"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_REPORTS = "export_reports"
    MANAGE_PIPELINES = "manage_pipelines"
    VIEW_AUDIT_LOGS = "view_audit_logs"


ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: set(Permission),
    Role.DEVELOPER: {
        Permission.CONNECT_REPOS,
        Permission.RUN_PIPELINES,
        Permission.VIEW_VULNERABILITIES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_REPORTS,
    },
    Role.SECURITY_ANALYST: {
        Permission.VIEW_VULNERABILITIES,
        Permission.SUPPRESS_VULNERABILITIES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_REPORTS,
    },
    Role.MANAGER: {
        Permission.VIEW_VULNERABILITIES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_REPORTS,
    },
}


def has_permission(role: str, permission: Permission) -> bool:
    try:
        role_enum = Role(role)
    except ValueError:
        return False
    return permission in ROLE_PERMISSIONS.get(role_enum, set())
