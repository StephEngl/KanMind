from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow full access if the user is the owner
        if obj.owner == request.user:
            return True
        # Allow read-only access if the user is a member
        return request.method in SAFE_METHODS and request.user in obj.members.all()