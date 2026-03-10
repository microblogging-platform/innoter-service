from drf_spectacular.extensions import OpenApiAuthenticationExtension

from src.apps.users.authentication import JWTAuthentication


class JWTScheme(OpenApiAuthenticationExtension):
    target_class = JWTAuthentication
    name = "JWTAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
