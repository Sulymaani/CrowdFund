"""
Custom permissions for Campaign API.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the campaign
        # or staff members
        return (obj.creator == request.user or 
                request.user.is_staff or 
                (hasattr(obj, 'organization') and 
                 obj.organization and 
                 request.user in obj.organization.users.all()))
