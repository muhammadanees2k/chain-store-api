from djoser.views import UserViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view
from core.serializers import UserCreateSerializer # Import your serializer

@extend_schema_view(
    create=extend_schema(request=UserCreateSerializer, responses=UserCreateSerializer),
)

class CustomUserViewSet(UserViewSet):
    """
    Custom ViewSet to hide unnecessary Djoser endpoints from the Swagger UI.
    """

    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        # Hides GET /auth/users/ (We don't want public users seeing a list of everyone)
        return super().list(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        # Hides GET /auth/users/{id}/
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def set_username(self, request, *args, **kwargs):
        return super().set_username(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def reset_username(self, request, *args, **kwargs):
        return super().reset_username(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def reset_username_confirm(self, request, *args, **kwargs):
        return super().reset_username_confirm(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def activation(self, request, *args, **kwargs):
        return super().activation(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def resend_activation(self, request, *args, **kwargs):
        return super().resend_activation(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        # Hides PUT /auth/users/{id}/
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        # Hides PATCH /auth/users/{id}/
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        # Hides DELETE /auth/users/{id}/
        return super().destroy(request, *args, **kwargs)
