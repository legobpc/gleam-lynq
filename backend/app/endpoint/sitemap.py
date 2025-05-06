from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import httpx
import xml.etree.ElementTree as ET
import gzip
from io import BytesIO

router = APIRouter(
    prefix="",
    tags=["Sitemap Checker"]
)


class SitemapCheckInput(BaseModel):
    domain: str = Field(
        ...,
        description="The domain or full URL to check sitemap.xml for. If missing scheme, 'https://' will be added automatically.",
        json_schema_extra={"example": "example.com"}
    )

    @field_validator('domain')
    def ensure_scheme(cls, v):
        """
        Ensures the domain starts with http:// or https://.
        Defaults to https:// if missing.
        """
        if not v.startswith(('http://', 'https://')):
            return 'https://' + v
        return v


class SitemapFetchInput(BaseModel):
    sitemap_url: str = Field(
        ...,
        description="Full URL of the sitemap to fetch and parse.",
        json_schema_extra={"example": "https://example.com/sitemap1.xml.gz"}
    )


class SitemapCheckResponse(BaseModel):
    sitemap_url: str
    sitemap_status: str
    http_status: Optional[int]
    sitemap_files: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)  # 👈 додаємо для <urlset>
    message: str


class SitemapURLsResponse(BaseModel):
    sitemap_url: str
    sitemap_status: str
    http_status: Optional[int]
    urls: List[str] = Field(default_factory=list)
    message: str


@router.post(
    "/check-sitemap",
    summary="Check sitemap.xml status and list nested sitemap files or direct URLs",
    response_description="Returns sitemap files (from sitemapindex) or direct URLs (from urlset).",
    response_model=SitemapCheckResponse
)
async def check_sitemap(data: SitemapCheckInput):
    """
    🛠 Main endpoint that:

    1️⃣ Builds the sitemap URL (domain + /sitemap.xml).
    2️⃣ Downloads and parses the sitemap file.
    3️⃣ If it's <sitemapindex>: returns a list of nested sitemap files.
    4️⃣ If it's <urlset>: returns URLs directly.
    """
    sitemap_url = data.domain.rstrip('/') + '/sitemap.xml'
    sitemap_files = []
    urls = []

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(sitemap_url)
            status_code = resp.status_code

            if status_code >= 400:
                return SitemapCheckResponse(
                    sitemap_url=sitemap_url,
                    sitemap_status="Not Found",
                    http_status=status_code,
                    sitemap_files=[],
                    urls=[],
                    message=f"Sitemap returned status {status_code}."
                )

            sitemap_status = "Found"
            message = f"Sitemap is available (status {status_code})."

            try:
                root = ET.fromstring(resp.content)

                if root.tag.endswith('urlset'):
                    urls = [elem.text for elem in root.findall('.//{*}url/{*}loc')]
                    message += f" This is a <urlset> sitemap. Found {len(urls)} URLs."

                elif root.tag.endswith('sitemapindex'):
                    sitemap_files = [elem.text for elem in root.findall('.//{*}sitemap/{*}loc')]
                    message += f" Found {len(sitemap_files)} nested sitemap files."

                else:
                    sitemap_status = "Unsupported format"
                    message = "Sitemap XML has unsupported root element."

            except ET.ParseError:
                sitemap_status = "Parse Error"
                message = "Failed to parse sitemap XML."

            return SitemapCheckResponse(
                sitemap_url=sitemap_url,
                sitemap_status=sitemap_status,
                http_status=status_code,
                sitemap_files=sitemap_files,
                urls=urls,
                message=message
            )

    except httpx.RequestError as exc:
        return SitemapCheckResponse(
            sitemap_url=sitemap_url,
            sitemap_status="Error",
            http_status=None,
            sitemap_files=[],
            urls=[],
            message=f"Request error: {exc}"
        )


@router.post(
    "/fetch-sitemap-urls",
    summary="Fetch and parse URLs from a specific sitemap file",
    response_description="Returns all <loc> URLs from a sitemap file (supports .xml and .xml.gz).",
    response_model=SitemapURLsResponse
)
async def fetch_sitemap_urls(data: SitemapFetchInput):
    """
    📥 Fetches and parses a given sitemap file:

    ✅ Supports normal XML and gzipped XML (.gz).
    ✅ Extracts all <loc> URLs inside <url> elements.
    """
    urls = []

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(data.sitemap_url)
            status_code = resp.status_code
            content = resp.content

            if status_code >= 400:
                return SitemapURLsResponse(
                    sitemap_url=data.sitemap_url,
                    sitemap_status="Not Found",
                    http_status=status_code,
                    urls=[],
                    message=f"Sitemap file returned status {status_code}."
                )

            # Detect gzip by magic bytes (0x1f 0x8b)
            is_gzip = content[:2] == b'\x1f\x8b'
            if is_gzip:
                try:
                    with gzip.GzipFile(fileobj=BytesIO(content)) as f:
                        content = f.read()
                except Exception as e:
                    return SitemapURLsResponse(
                        sitemap_url=data.sitemap_url,
                        sitemap_status="Decompression Failed",
                        http_status=status_code,
                        urls=[],
                        message=f"Failed to decompress gzip sitemap: {e}"
                    )

            try:
                root = ET.fromstring(content)
                urls = [elem.text for elem in root.findall('.//{*}url/{*}loc')]
                msg = f"Parsed {len(urls)} URLs from sitemap."
                sitemap_status = "Parsed"
            except ET.ParseError as e:
                msg = f"Failed to parse sitemap XML: {e}"
                sitemap_status = "Parse Error"

            return SitemapURLsResponse(
                sitemap_url=data.sitemap_url,
                sitemap_status=sitemap_status,
                http_status=status_code,
                urls=urls,
                message=msg
            )

    except httpx.RequestError as exc:
        return SitemapURLsResponse(
            sitemap_url=data.sitemap_url,
            sitemap_status="Error",
            http_status=None,
            urls=[],
            message=f"Request error: {exc}"
        )
