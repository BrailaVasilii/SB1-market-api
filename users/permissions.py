from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Permission class to check if user is in moderators group"""
    
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.groups.filter(name='moderators').exists()
        )


class IsOwner(permissions.BasePermission):
    """Permission class to check if user is owner of the object"""
    
    def has_object_permission(self, request, view, obj):
        # Check if object has owner field and user is the owner
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsOwnerOrModerator(permissions.BasePermission):
    """Permission class to check if user is owner or moderator"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Moderators can access any object
        if request.user.groups.filter(name='moderators').exists():
            return True
            
        # Owners can access their own objects
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsModeratorReadOnly(permissions.BasePermission):
    """Permission for moderators - read and update only, no create/delete"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        # Check if user is moderator
        is_moderator = request.user.groups.filter(name='moderators').exists()
        
        if is_moderator:
            # Moderators can only view and update, not create or delete
            return view.action in ['list', 'retrieve', 'update', 'partial_update']
        
        return True  # Non-moderators handled by other permissions