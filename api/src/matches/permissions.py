from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return (
            request.user
            and request.user.is_authenticated
            and obj.author == request.user.player.discord_user
        )
