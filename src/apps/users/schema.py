from drf_spectacular.extensions import OpenApiAuthenticationExtension

from apps.users.authentication import UserManagementAuthentication


class JWTScheme(OpenApiAuthenticationExtension):
    target_class = UserManagementAuthentication
    name = "UserManagementAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
