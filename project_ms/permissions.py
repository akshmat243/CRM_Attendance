from rest_framework.exceptions import PermissionDenied


class RolePermissionMixin:
    """
    Centralized role-based permission logic
    """

    allowed_roles = []

    def has_role_permission(self, user):
        return user.role in self.allowed_roles
