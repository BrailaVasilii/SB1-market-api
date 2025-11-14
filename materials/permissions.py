from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission для владельцев объектов
    Owner может редактировать/удалять свои объекты
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions только для owner
        return obj.author == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission для владельцев или администраторов
    - Owner может редактировать/удалять свои объекты
    - Admin может редактировать/удалять любые объекты
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions для owner или admin
        return obj.author == request.user or request.user.role == "admin"
