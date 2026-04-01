import logging
from datetime import datetime
from uuid import UUID

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import User

logger = logging.getLogger(__name__)


def _parse_dt(value: object) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _extract_group_id(group: object) -> int | None:
    if group is None:
        return None
    if isinstance(group, int):
        return group
    if isinstance(group, str) and group.isdigit():
        return int(group)
    if isinstance(group, dict):
        for key in ("id", "group_id"):
            value = group.get(key)
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.isdigit():
                return int(value)
    # TODO: Align response shape with user-management service contract.
    return None


class UserManagementAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request) -> tuple[User, dict] | None:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) == 0 or parts[0] != self.keyword or len(parts) != 2:
            return None

        if not getattr(settings, "USER_MANAGEMENT_BASE_URL", None):
            logger.error("USER_MANAGEMENT_BASE_URL is not configured")
            raise AuthenticationFailed("Authentication service is not configured")

        try:
            import httpx

            url = "http://user-management-service:8000/api/v1/users/me"
            timeout = 3

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

        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        role = payload.get("role")
        group_id = _extract_group_id(payload.get("group"))

        if not user_id:
            raise AuthenticationFailed("User id is missing in token")
        if not role:
            raise AuthenticationFailed("Role is missing in token")

        try:
            user_uuid = UUID(str(user_id))
        except Exception:
            raise AuthenticationFailed("Invalid user id")

        user = User(
            id=user_uuid,
            role=str(role),
            group_id=group_id,
            name=payload.get("name"),
            surname=payload.get("surname"),
            username=payload.get("username"),
            phone_number=payload.get("phone_number") or payload.get("phoneNumber"),
            email=payload.get("email"),
            image_s3_path=payload.get("image_s3_path") or payload.get("imageS3Path"),
            is_blocked=payload.get("is_blocked") if "is_blocked" in payload else payload.get("isBlocked"),
            created_at=_parse_dt(payload.get("created_at") or payload.get("createdAt")),
        )

        return user, payload

    def authenticate_header(self, request) -> str:
        return self.keyword