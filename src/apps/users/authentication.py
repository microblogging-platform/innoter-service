import uuid
import jwt
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from src.apps.users.models import User

logger = logging.getLogger(__name__)

class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request) -> tuple[User, dict] | None:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) == 0 or parts[0] != self.keyword or len(parts) != 2:
            return None

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True}
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid payload data: {e}")
            raise AuthenticationFailed("Invalid payload structure")
        except Exception as e:
            logger.error(f"Unexpected JWT error: {e}")
            raise AuthenticationFailed("Authentication failed")

        user = User(
            id=payload.get("sub"),
            role=payload.get("role"),
            group_id=payload.get("group_id")
        )

        return user, payload

    def authenticate_header(self, request) -> str:
        return self.keyword