from fastapi import APIRouter
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, List
import httpx
from bs4 import BeautifulSoup

router = APIRouter(
    prefix="",
    tags=["URL Checker"]
)

# ✅ Schema for alternate hreflang items
class AlternateHreflang(BaseModel):
    hreflang: str
    href: str

# ✅ Schema for headings (H1-H6)
class HeadingTag(BaseModel):
    tag: str
    text: str

# ✅ Response model
class URLCheckResponse(BaseModel):
    url: str
    http_status: Optional[int]
    redirected: bool
    final_url: Optional[str]
    title: Optional[str]
    description: Optional[str]
    canonical: Optional[str]
    canonical_matches: Optional[bool]
    h1: Optional[str]
    all_h1: List[str]
    headings: List[HeadingTag]
    robots_meta: Optional[str]
    x_robots_tag: Optional[str]
    content_type: Optional[str]
    content_length: Optional[int]
    headers: Dict[str, str]
    open_graph: Dict[str, str]
    twitter_meta: Dict[str, str]
    schema_json_ld: Optional[str]
    alternate_hreflang: List[AlternateHreflang]
    lang: Optional[str]
    favicon_url: Optional[str]
    message: str

# ✅ Input model
class URLCheckInput(BaseModel):
    url: HttpUrl = Field(..., json_schema_extra={"example": "https://example.com/page"})

# ✅ Main endpoint
@router.post(
    "/check-url",
    summary="Check technical and SEO data for a URL",
    response_description="Returns technical status and SEO-related information for the given URL.",
    response_model=URLCheckResponse
)
async def check_url(data: URLCheckInput):
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            response = await client.get(str(data.url))
            status_code = response.status_code
            redirected = len(response.history) > 0
            final_url = str(response.url)
            headers = {k: v for k, v in response.headers.items()}
            content_type = headers.get('Content-Type')

            # Safer content-length parsing
            content_length_raw = headers.get('Content-Length')
            try:
                content_length = int(content_length_raw) if content_length_raw else None
            except ValueError:
                content_length = None

            x_robots_tag = headers.get('X-Robots-Tag')

            # Initialize fields
            title = description = canonical = robots_meta = schema_json_ld = lang = favicon_url = None
            h1 = None
            canonical_matches = None
            all_h1 = []
            headings = []
            alternate_hreflang = []
            open_graph = {}
            twitter_meta = {}

            # Decide if we should parse the HTML
            should_parse_html = False
            if content_type and 'text/html' in content_type.lower():
                should_parse_html = True
            elif not content_type:
                text_snippet = response.text.strip().lower()
                if text_snippet.startswith('<!doctype html') or text_snippet.startswith('<html'):
                    should_parse_html = True

            if should_parse_html:
                # ✅ Use 'lxml' parser here
                soup = BeautifulSoup(response.text, 'lxml')

                # ✅ Title
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()

                # ✅ Meta description
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                if desc_tag and desc_tag.has_attr('content'):
                    description = desc_tag['content'].strip()

                # ✅ Meta robots
                robots_tag = soup.find('meta', attrs={'name': 'robots'})
                if robots_tag and robots_tag.has_attr('content'):
                    robots_meta = robots_tag['content'].strip()

                # ✅ Canonical link
                canonical_tag = soup.find('link', rel='canonical')
                if canonical_tag and canonical_tag.has_attr('href'):
                    canonical = canonical_tag['href'].strip()

                # ✅ Check if canonical matches the final URL
                canonical_matches = (canonical == final_url) if canonical else None

                # ✅ Open Graph tags
                og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
                for tag in og_tags:
                    if tag.has_attr('property') and tag.has_attr('content'):
                        prop = tag['property']
                        content = tag['content']
                        open_graph[prop] = content.strip()

                # ✅ Twitter meta tags
                twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
                for tag in twitter_tags:
                    if tag.has_attr('name') and tag.has_attr('content'):
                        name = tag['name']
                        content = tag['content']
                        twitter_meta[name] = content.strip()

                # ✅ All H1 tags
                h1_tags = [tag.get_text(strip=True) for tag in soup.find_all('h1')]
                all_h1 = h1_tags
                h1 = h1_tags[0] if h1_tags else None

                # ✅ Full headings structure (H1-H6)
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    headings.append(HeadingTag(
                        tag=tag.name,
                        text=tag.get_text(strip=True)
                    ))

                # ✅ JSON-LD Schema
                json_ld_tag = soup.find('script', type='application/ld+json')
                if json_ld_tag and json_ld_tag.string:
                    schema_json_ld = json_ld_tag.string.strip()

                # ✅ Alternate hreflang tags
                for link in soup.find_all('link', rel='alternate'):
                    if link.has_attr('hreflang') and link.has_attr('href'):
                        hreflang = link['hreflang']
                        href = link['href']
                        alternate_hreflang.append(AlternateHreflang(
                            hreflang=hreflang.strip(),
                            href=href.strip()
                        ))

                # ✅ HTML lang attribute
                html_tag = soup.find('html')
                if html_tag and html_tag.has_attr('lang'):
                    lang = html_tag['lang'].strip()

                # ✅ Favicon
                favicon_tag = soup.find('link', rel=lambda x: x and 'icon' in x)
                if favicon_tag and favicon_tag.has_attr('href'):
                    favicon_url = favicon_tag['href'].strip()

            message = f"URL checked successfully. Status: {status_code}"

            return URLCheckResponse(
                url=str(data.url),
                http_status=status_code,
                redirected=redirected,
                final_url=final_url,
                title=title,
                description=description,
                canonical=canonical,
                canonical_matches=canonical_matches,
                h1=h1,
                all_h1=all_h1,
                headings=headings,
                robots_meta=robots_meta,
                x_robots_tag=x_robots_tag,
                content_type=content_type,
                content_length=content_length,
                headers=headers,
                open_graph=open_graph,
                twitter_meta=twitter_meta,
                schema_json_ld=schema_json_ld,
                alternate_hreflang=alternate_hreflang,
                lang=lang,
                favicon_url=favicon_url,
                message=message
            )

        except httpx.RequestError as e:
            return URLCheckResponse(
                url=str(data.url),
                http_status=None,
                redirected=False,
                final_url=None,
                title=None,
                description=None,
                canonical=None,
                canonical_matches=None,
                h1=None,
                all_h1=[],
                headings=[],
                robots_meta=None,
                x_robots_tag=None,
                content_type=None,
                content_length=None,
                headers={},
                open_graph={},
                twitter_meta={},
                schema_json_ld=None,
                alternate_hreflang=[],
                lang=None,
                favicon_url=None,
                message=f"Request failed: {str(e)}"
            )
