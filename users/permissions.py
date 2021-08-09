from rest_framework import permissions

class isFundraiser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user.role == "FUNDRAISER") or 
            (request.method in permissions.SAFE_METHODS)
        )