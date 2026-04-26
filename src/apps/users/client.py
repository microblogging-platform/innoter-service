import asyncio
import logging
from typing import Iterable

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


async def fetch_author_info(user_id: str, auth_header: str | None = None) -> dict | None:
    base_url = getattr(settings, "USER_MANAGEMENT_BASE_URL", None)
    if not base_url:
        return None
    path = settings.USER_MANAGEMENT_AUTHOR_INFO_PATH.format(user_id=user_id)
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    timeout = settings.USER_MANAGEMENT_TIMEOUT_SECONDS
    headers = {"Authorization": auth_header} if auth_header else {}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        logger.warning("author-info %s returned %s", url, resp.status_code)
    except Exception as e:
        logger.warning("Failed to fetch author info for %s: %s", user_id, e)
    return None


async def fetch_author_info_map(user_ids: Iterable[str], auth_header: str | None = None) -> dict[str, dict]:
    unique_ids = list({str(uid) for uid in user_ids})
    if not unique_ids:
        return {}
    results = await asyncio.gather(*[fetch_author_info(uid, auth_header) for uid in unique_ids])
    return {uid: info for uid, info in zip(unique_ids, results) if info}
