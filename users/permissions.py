from rest_framework import permissions


class isFundraiser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.role == "FUNDRAISER")


class IsDonatur(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return bool(request.user.role == "DONATUR")
