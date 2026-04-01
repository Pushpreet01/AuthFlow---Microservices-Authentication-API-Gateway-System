import httpx
from fastapi import Request

async def forward_request(service_url: str, path: str, method: str, request: Request, data=None, cookies=None):
    url = f"{service_url}{path}"

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in ("host", "content-length", "transfer-encoding")
    }

    cookies = dict(request.cookies) if cookies is None else cookies

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            json=data,
            headers=headers,
            cookies=cookies
        )

        return response