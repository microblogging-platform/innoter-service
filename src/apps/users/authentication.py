import logging
from datetime import datetime
from uuid import UUID

import httpx
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import User

logger = logging.getLogger(__name__)


class UserManagementAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request) -> tuple[User, dict] | None:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        base_url = getattr(settings, "USER_MANAGEMENT_BASE_URL", None)
        if not base_url:
            logger.error("USER_MANAGEMENT_BASE_URL is not configured")
            raise AuthenticationFailed("Authentication service is not configured")

        url = base_url.rstrip("/") + "/" + settings.USER_MANAGEMENT_ME_PATH.lstrip("/")
        timeout = settings.USER_MANAGEMENT_TIMEOUT_SECONDS

        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.get(url, headers={"Authorization": auth_header})

            if resp.status_code in (401, 403):
                raise AuthenticationFailed("Invalid token")
            if resp.status_code >= 500:
                logger.warning("user-management /users/me failed: %s %s", resp.status_code, resp.text)
                raise AuthenticationFailed("Authentication service error")
            if resp.status_code != 200:
                logger.warning("Unexpected /users/me response: %s %s", resp.status_code, resp.text)
                raise AuthenticationFailed("Authentication failed")

            payload = resp.json()
        except AuthenticationFailed:
            raise
        except Exception as e:
            logger.error("user-management auth request failed: %s", e)
            raise AuthenticationFailed("Authentication service unavailable")

        user_id = payload.get("id") or payload.get("sub")
        role = payload.get("role")
        group_id = payload.get("group_id")

        if not user_id:
            raise AuthenticationFailed("User id is missing in response")
        if not role:
            raise AuthenticationFailed("Role is missing in response")

        try:
            user_uuid = UUID(str(user_id))
        except ValueError:
            raise AuthenticationFailed("Invalid user id format")

        created_at = payload.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except ValueError:
                created_at = None

        user = User(
            id=user_uuid,
            role=str(role),
            group_id=group_id,
            name=payload.get("name"),
            surname=payload.get("surname"),
            username=payload.get("username"),
            phone_number=payload.get("phone_number"),
            email=payload.get("email"),
            image_s3_path=payload.get("image_s3_path"),
            created_at=created_at,
        )

        return user, payload

    def authenticate_header(self, request) -> str:
        return self.keyword
