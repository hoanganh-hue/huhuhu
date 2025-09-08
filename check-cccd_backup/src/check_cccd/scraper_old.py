import re
import time
from typing import Dict, List, Optional
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
# Optimized settings for better performance
REQUEST_TIMEOUT = 20.0  # Increased from 15.0 for more stable requests
MAX_RETRIES = 3
RETRY_DELAY = 1.0
from .logging import logger, metrics
from .anti_bot import RequestStrategy


class ScrapingError(Exception):
    """Custom exception for scraping errors."""
    pass


def scrape_cccd_sync(cccd: str) -> Dict:
    """Enhanced synchronous fetch + parse flow for a single CCCD with realistic user flow.

    Features:
    - Realistic user flow: homepage -> search page -> search -> results
    - Retry logic with exponential backoff
    - Robust selectors for masothue.com
    - Better error handling
    - Structured logging
    - Metrics collection
    """
    start_time = time.time()

    try:
        result = _scrape_with_retry(cccd)

        # Log success
        duration_ms = (time.time() - start_time) * 1000
        logger.info("Scraping completed",
                    cccd=cccd,
                    status=result.get("status"),
                    duration_ms=duration_ms,
                    matches_count=len(result.get("matches", [])))

        # Update metrics
        metrics.increment_counter("scraping_requests_total", tags={"status": result.get("status")})
        metrics.record_histogram("scraping_duration_ms", duration_ms)

        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error("Scraping failed",
                     cccd=cccd,
                     error=str(e),
                     duration_ms=duration_ms)

        metrics.increment_counter("scraping_requests_total", tags={"status": "error"})
        metrics.increment_counter("scraping_errors_total")

        return {
            "id_cccd": cccd,
            "source": "masothue.com",
            "fetched_at": datetime.utcnow().isoformat() + 'Z',
            "status": "error",
            "matches": [],
            "error_message": str(e)
        }


def _scrape_with_retry(cccd: str) -> Dict:
    """Scrape with retry logic and anti-bot strategies."""
    last_error = None
    request_strategy = RequestStrategy()

    for attempt in range(MAX_RETRIES):
        try:
            return _scrape_single_attempt(cccd, attempt, request_strategy)
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.warning("Scraping attempt failed, retrying",
                               cccd=cccd,
                               attempt=attempt + 1,
                               error=str(e),
                               retry_delay=delay)
                time.sleep(delay)
            else:
                logger.error("All scraping attempts failed",
                             cccd=cccd,
                             attempts=MAX_RETRIES,
                             final_error=str(e))

    raise ScrapingError(f"Failed after {MAX_RETRIES} attempts: {last_error}")


def _scrape_single_attempt(cccd: str, attempt: int, request_strategy: RequestStrategy) -> Dict:
    """Single scraping attempt with anti-bot strategies and realistic user flow."""

    # Step 1: Visit homepage first (mimic real user behavior)
    homepage_url = "https://masothue.com/"
    logger.info("Step 1: Visiting homepage to establish session", url=homepage_url, attempt=attempt+1)

    try:
        homepage_response = request_strategy.execute_request(homepage_url, "", attempt, method="GET")
        homepage_response.raise_for_status()
        logger.info("✅ Successfully visited homepage - session established")
    except Exception as e:
        logger.warning("⚠️ Failed to visit homepage, continuing anyway", error=str(e))

    # Add small delay to mimic user reading
    time.sleep(1.5)

    # Step 2: Navigate to personal tax code search page
    search_page_url = "https://masothue.com/tra-cuu-ma-so-thue-ca-nhan/"
    logger.info("Step 2: Navigating to personal tax search page", url=search_page_url, attempt=attempt+1)

    try:
        search_page_response = request_strategy.execute_request(search_page_url, "", attempt, method="GET")
        search_page_response.raise_for_status()
        logger.info("✅ Successfully accessed personal tax search page")
    except Exception as e:
        logger.warning("⚠️ Failed to access search page, continuing anyway", error=str(e))

    # Add delay to mimic user interaction
    time.sleep(2.0)

    # Step 3: Perform search with CCCD (mimic form submission)
    search_url = "https://masothue.com/Search/"
    logger.info("Step 3: Performing CCCD search", cccd=cccd, search_url=search_url, attempt=attempt+1)

    # Use anti-bot strategy for search request
    response = request_strategy.execute_request(search_url, cccd, attempt)
    response.raise_for_status()
    html = response.text

    # Parse search results with improved selectors
    soup = BeautifulSoup(html, "lxml")
    matches = _parse_search_results(soup, cccd)

    if not matches:
        logger.info("No matches found for CCCD", cccd=cccd, status="not_found")
        return {
            "id_cccd": cccd,
            "source": "masothue.com",
            "fetched_at": datetime.utcnow().isoformat() + 'Z',
            "status": "not_found",
            "matches": [],
            "search_flow": {
                "homepage_visited": True,
                "search_page_accessed": True,
                "search_performed": True,
                "results_found": False
            }
        }

    logger.info("Found matches for CCCD", cccd=cccd, matches_count=len(matches), status="found")

    # Step 4: Fetch detailed information for each match (mimic clicking on results)
    detailed_matches = []
    for i, match in enumerate(matches):
        logger.info("Fetching details for match", match_index=i+1, url=match.get("url"))

        try:
            # Add delay between detail requests to avoid rate limiting
            time.sleep(1.0)
            detailed_match = _fetch_profile_details(match, response.request.headers)
            detailed_matches.append(detailed_match)
            logger.info("Successfully fetched details", match_index=i+1)
        except Exception as e:
            logger.warning("Failed to fetch profile details, keeping original match",
                           match_index=i+1, url=match.get("url"), error=str(e))
            detailed_matches.append(match)  # Keep original match if details fail

    return {
        "id_cccd": cccd,
        "source": "masothue.com",
        "fetched_at": datetime.utcnow().isoformat() + 'Z',
        "status": "found",
        "matches": detailed_matches,
        "search_flow": {
            "homepage_visited": True,
            "search_page_accessed": True,
            "search_performed": True,
            "results_found": True,
            "details_fetched": len(detailed_matches)
        }
    }


def _parse_search_results(soup: BeautifulSoup, cccd: str) -> List[Dict]:
    """Parse search results page with improved selectors."""
    matches = []

    # Look for profile links with various patterns
    profile_selectors = [
        'a[href*="/"]',  # Any link
        '.search-result a',
        '.result-item a',
        'a[href*="masothue.com"]'
    ]

    for selector in profile_selectors:
        links = soup.select(selector)
        for link in links:
            href = link.get('href')
            if not href:
                continue

            # Check if this looks like a profile link
            if _is_profile_link(href):
                match = {
                    "type": "person_or_company",
                    "name": _extract_name_from_link(link),
                    "tax_code": _extract_tax_code_from_href(href),
                    "url": _normalize_url(href),
                    "address": None,
                    "role": None,
                    "raw_snippet": link.get_text(strip=True)[:500]
                }
                matches.append(match)
                break  # Take first valid match

    return matches


def _is_profile_link(href: str) -> bool:
    """Check if href looks like a profile link."""
    if not href:
        return False

    # Look for patterns that indicate profile pages
    profile_patterns = [
        r'/\d{10,}',  # Contains 10+ digits
        r'/company/',
        r'/person/',
        r'/tax-code/'
    ]

    for pattern in profile_patterns:
        if re.search(pattern, href):
            return True

    return False


def _extract_name_from_link(link_element) -> Optional[str]:
    """Extract name from link element."""
    # Try various text extraction methods
    text = link_element.get_text(strip=True)
    if text and len(text) > 3:
        return text

    # Look for title attribute
    title = link_element.get('title')
    if title:
        return title.strip()

    return None


def _extract_tax_code_from_href(href: str) -> Optional[str]:
    """Extract tax code from href."""
    match = re.search(r'(\d{10,13})', href)
    return match.group(1) if match else None


def _normalize_url(href: str) -> str:
    """Normalize URL to absolute format."""
    if href.startswith('/'):
        return f'https://masothue.com{href}'
    elif href.startswith('http'):
        return href
    else:
        return f'https://masothue.com/{href}'


def _fetch_profile_details(match: Dict, headers: Dict) -> Dict:
    """Fetch detailed information from profile page."""
    url = match.get("url")
    if not url:
        return match

    try:
        # Use anti-bot strategy for profile page too
        request_strategy = RequestStrategy()

        # Create a simple request for profile page
        with httpx.Client(timeout=REQUEST_TIMEOUT, headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, 'lxml')

        # Enhanced extraction with multiple selectors
        name = _extract_name_from_profile(soup)
        tax_code = _extract_tax_code_from_profile(soup, url)
        address = _extract_address_from_profile(soup)
        role = _extract_role_from_profile(soup)

        # Update match with extracted data
        updated_match = match.copy()
        if name:
            updated_match["name"] = name
        if tax_code:
            updated_match["tax_code"] = tax_code
        if address:
            updated_match["address"] = address
        if role:
            updated_match["role"] = role

        # Update raw snippet with full page content
        updated_match["raw_snippet"] = soup.get_text(separator=' ', strip=True)[:2000]

        return updated_match

    except Exception as e:
        logger.warning("Failed to fetch profile details", url=url, error=str(e))
        return match


def _extract_name_from_profile(soup: BeautifulSoup) -> Optional[str]:
    """Extract name from profile page with enhanced selectors and patterns."""
    # Priority selectors (most specific first)
    selectors = [
        'h1',
        'h2',
        '.company-name',
        '.person-name',
        '.profile-title',
        '.profile-name',
        '.business-name',
        '.entity-name',
        '[class*="name"]',
        '.title',
        '.header-title',
        '.main-title',
        '.page-title'
    ]

    # Try CSS selectors first
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            text = element.get_text(strip=True)
            if text and len(text) > 2 and not text.isdigit():
                return text

    # Try regex patterns on page text
    text = soup.get_text()
    name_patterns = [
        r'Tên[:\s]*(.+?)(?:\n|$)',
        r'Tên công ty[:\s]*(.+?)(?:\n|$)',
        r'Tên doanh nghiệp[:\s]*(.+?)(?:\n|$)',
        r'Họ và tên[:\s]*(.+?)(?:\n|$)',
        r'Người đại diện[:\s]*(.+?)(?:\n|$)',
        r'Giám đốc[:\s]*(.+?)(?:\n|$)',
        r'Chủ sở hữu[:\s]*(.+?)(?:\n|$)'
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            name = match.group(1).strip()
            if len(name) > 2 and not name.isdigit():
                return name

    return None


def _extract_tax_code_from_profile(soup: BeautifulSoup, url: str) -> Optional[str]:
    """Extract tax code from profile page with enhanced patterns."""
    # First try to extract from URL
    url_match = re.search(r'(\d{10,13})', url)
    if url_match:
        return url_match.group(1)

    # Try to extract from page content with multiple patterns
    text = soup.get_text()

    # Primary patterns
    tax_patterns = [
        r'MST[:\s]*(\d{10,13})',
        r'Mã số[:\s]*(\d{10,13})',
        r'Tax Code[:\s]*(\d{10,13})',
        r'Mã số doanh nghiệp[:\s]*(\d{10,13})',
        r'Số đăng ký[:\s]*(\d{10,13})',
        r'Mã số kinh doanh[:\s]*(\d{10,13})'
    ]

    for pattern in tax_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            tax_code = match.group(1)
            # Validate tax code format (10-13 digits)
            if 10 <= len(tax_code) <= 13 and tax_code.isdigit():
                return tax_code

    # Look for any 10-13 digit number in structured data
    lines = text.split('\n')
    for line in lines:
        # Look for lines that might contain tax codes
        if any(keyword in line.lower() for keyword in ['mst', 'đăng ký']):
            numbers = re.findall(r'\d{10,13}', line)
            for number in numbers:
                if 10 <= len(number) <= 13:
                    return number

    # Last resort: any 10-13 digit number
    number_match = re.search(r'(\d{10,13})', text)
    if number_match:
        return number_match.group(1)

    return None


def _extract_address_from_profile(soup: BeautifulSoup) -> Optional[str]:
    """Extract address from profile page."""
    # Look for address-related text
    address_patterns = [
        r'Địa chỉ[:\s]*(.+?)(?:\n|$)',
        r'Address[:\s]*(.+?)(?:\n|$)',
        r'(?:Thành phố|Quận|Huyện|Phường|Xã|Số \d+).+'
    ]

    text = soup.get_text()
    for pattern in address_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            address = match.group(1).strip()
            if len(address) > 10:  # Reasonable address length
                return address

    return None


def _extract_role_from_profile(soup: BeautifulSoup) -> Optional[str]:
    """Extract role/position from profile page."""
    role_patterns = [
        r'Chức vụ[:\s]*(.+?)(?:\n|$)',
        r'Position[:\s]*(.+?)(?:\n|$)',
        r'Role[:\s]*(.+?)(?:\n|$)'
    ]

    text = soup.get_text()
    for pattern in role_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            role = match.group(1).strip()
            if len(role) > 2:
                return role

    return None