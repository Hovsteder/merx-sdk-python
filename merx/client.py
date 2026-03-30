import json
from typing import Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from .types import MerxError

DEFAULT_BASE_URL = "https://merx.exchange"


class HttpClient:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    def get(self, path: str) -> Any:
        req = Request(
            f"{self._base_url}{path}",
            headers={"x-api-key": self._api_key},
        )
        return self._send(req)

    def post(
        self,
        path: str,
        payload: dict,
        extra_headers: Optional[dict] = None,
    ) -> Any:
        data = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self._api_key,
        }
        if extra_headers:
            headers.update(extra_headers)
        req = Request(
            f"{self._base_url}{path}",
            data=data,
            headers=headers,
            method="POST",
        )
        return self._send(req)

    def delete(self, path: str) -> Any:
        req = Request(
            f"{self._base_url}{path}",
            headers={"x-api-key": self._api_key},
            method="DELETE",
        )
        return self._send(req)

    def _send(self, req: Request) -> Any:
        try:
            with urlopen(req) as resp:
                body = json.loads(resp.read())
        except HTTPError as exc:
            body = json.loads(exc.read())
            err = body.get("error", {})
            raise MerxError(
                err.get("code", "UNKNOWN"),
                err.get("message", "Request failed"),
            ) from exc

        if "error" in body:
            err = body["error"]
            raise MerxError(
                err.get("code", "UNKNOWN"),
                err.get("message", "Request failed"),
            )
        return body.get("data")
