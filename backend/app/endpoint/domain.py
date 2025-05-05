from fastapi import APIRouter
from pydantic import BaseModel, field_validator, Field
from typing import Optional, List
import httpx
import dns.resolver
import time

router = APIRouter(
    prefix="",
    tags=["Domain Checker"]
)

class DomainInput(BaseModel):
    domain: str = Field(
        ...,
        description="The domain or full URL to check. If the scheme (http/https) is missing, 'https://' will be added automatically.",
        json_schema_extra={"example": "test.com"}
    )

    @field_validator('domain')
    def ensure_scheme(cls, domain):
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        return domain

class DomainCheckResponse(BaseModel):
    fixed_domain: str
    dns_status: str
    http_status: Optional[int]
    is_live: bool
    redirected: Optional[bool]
    final_url: Optional[str]
    redirect_chain: List[str]
    response_time: Optional[float]
    message: str

@router.post(
    "/check-domain",
    summary="Check domain status",
    response_description="Detailed result of DNS and HTTP status for the provided domain.",
    response_model=DomainCheckResponse
)
async def check_domain(data: DomainInput):
    """
    **Overview:**

    This endpoint checks the status of a given domain or URL. It performs:

    - 🛜 **DNS lookup:** Validates if the domain has a valid A record.
    - 🌐 **HTTP request:** Sends an HTTP GET request to see if the website responds.
    - 🔄 **Redirect tracking:** Detects if there are any HTTP redirects and provides the full redirect chain.
    - ⚡ **Response timing:** Measures how long the HTTP request takes.

    **Returns:**

    - `fixed_domain`: The input domain with `https://` prepended if missing.
    - `dns_status`: Status of the DNS query (e.g., `ok`, `NXDOMAIN`, `DNS timeout`, `No A record`).
    - `http_status`: HTTP status code from the website (e.g., 200, 404, etc.).
    - `is_live`: `true` if the site returned a 200 OK response.
    - `redirected`: `true` if the request was redirected.
    - `final_url`: The final URL after all redirects.
    - `redirect_chain`: List of URLs that were followed during redirects.
    - `response_time`: Time taken (in seconds) for the HTTP request to complete.
    - `message`: Human-readable status message.

    **Example request:**

    ```json
    {
        "domain": "test.com"
    }
    ```
    """
    host_only = data.domain.replace('https://', '').replace('http://', '').rstrip('/')

    # 1️⃣ DNS check
    dns_status = "ok"
    try:
        dns.resolver.resolve(host_only, 'A')
    except dns.resolver.NXDOMAIN:
        dns_status = "NXDOMAIN"
    except dns.resolver.Timeout:
        dns_status = "DNS timeout"
    except dns.resolver.NoAnswer:
        dns_status = "No A record"

    if dns_status != "ok":
        return DomainCheckResponse(
            fixed_domain=data.domain,
            dns_status=dns_status,
            http_status=None,
            is_live=False,
            redirected=None,
            final_url=None,
            redirect_chain=[],
            response_time=None,
            message=f"DNS issue: {dns_status}"
        )

    # 2️⃣ HTTP check
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            start_time = time.perf_counter()
            response = await client.get(data.domain)
            end_time = time.perf_counter()

            status = response.status_code
            is_live = response.status_code == 200
            redirected = len(response.history) > 0
            final_url = str(response.url)
            redirect_chain = [str(r.url) for r in response.history]
            response_time = round(end_time - start_time, 3)  # in seconds

    except httpx.RequestError as exc:
        return DomainCheckResponse(
            fixed_domain=data.domain,
            dns_status=dns_status,
            http_status=None,
            is_live=False,
            redirected=None,
            final_url=None,
            redirect_chain=[],
            response_time=None,
            message=f"Connection error: {exc}"
        )

    return DomainCheckResponse(
        fixed_domain=data.domain,
        dns_status=dns_status,
        http_status=status,
        is_live=is_live,
        redirected=redirected,
        final_url=final_url,
        redirect_chain=redirect_chain,
        response_time=response_time,
        message=(
            "Domain is live and responded with 200"
            if is_live else f"Site returned status {status}"
        )
    )
