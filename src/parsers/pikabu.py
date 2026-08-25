"""Parser for Pikabu Courses (education.pikabu.ru).

Extracts course listings from the Pinia SSR state embedded in the page HTML,
with fallback to HTML card parsing. Data includes price, rating, reviews,
duration, school info, and course links.

The site is an Astro + Vue SSR app. Main data source is the Pinia initial
state JSON (via __piniaInitialState), which contains all structured course
data including fields not visible in the rendered HTML (rating stars, etc.).
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional
import re
import json
import time
import datetime

BASE_URL = "https://education.pikabu.ru"
COURSES_URL = f"{BASE_URL}/courses"

# Cache for resolved course URLs to avoid duplicate requests
_resolved_url_cache: Dict[str, str] = {}


def resolve_course_url(course_url: str, retries: int = 3, delay: float = 1.0) -> str:
    """Follow redirects to get the actual school course page URL.

    Pikabu uses internal redirect links (e.g., /c/abc123) that forward
    to the actual school's course page. This function follows the redirect
    and returns the final destination URL.

    Args:
        course_url: The pikabu internal course URL.
        retries: Number of retry attempts.
        delay: Delay between retries in seconds.

    Returns:
        The resolved final URL, or the original URL if resolution fails.
    """
    # Check cache first
    if course_url in _resolved_url_cache:
        return _resolved_url_cache[course_url]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    for attempt in range(retries):
        try:
            # Use allow_redirects=True to follow the redirect chain
            # We only need the final URL, not the content
            response = requests.head(
                course_url,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )
            # Get the final URL after all redirects
            final_url = response.url
            _resolved_url_cache[course_url] = final_url
            return final_url
        except requests.RequestException:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                # On failure, return original URL
                _resolved_url_cache[course_url] = course_url
                return course_url

    return course_url


def fetch_page(
    url: str, retries: int = 3, delay: float = 1.0
) -> Optional[BeautifulSoup]:
    """Fetch a page and return parsed HTML with retry logic.

    Args:
        url: The URL to fetch.
        retries: Number of retry attempts on failure.
        delay: Delay between retries in seconds.

    Returns:
        BeautifulSoup object if successful, None otherwise.

    Note:
        Use ``fetch_page_raw()`` to also get the raw response text for
        Pinia state extraction.
    """
    _, soup = fetch_page_raw(url, retries, delay)
    return soup


def fetch_page_raw(
    url: str, retries: int = 3, delay: float = 1.0
) -> tuple[Optional[str], Optional[BeautifulSoup]]:
    """Fetch a page, returning both raw text and parsed HTML.

    The raw text is needed for ``extract_page_context()`` which extracts
    JSON from a ``<script>`` tag before BeautifulSoup may alter it.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            raw_text = response.text
            soup = BeautifulSoup(response.content, "lxml")
            return raw_text, soup
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} after {retries} attempts: {e}")
                return None, None
    return None, None


def extract_text(element) -> str:
    """Safely extract and clean text from a BeautifulSoup element."""
    if element is None:
        return ""
    text = element.get_text(strip=True)
    if not text and element.string:
        text = element.string.strip()
    return text


def extract_page_context(html: str) -> Optional[dict]:
    """Extract the full page context JSON from the vike_pageContext script tag.

    The site embeds page data in:
      <script id="vike_pageContext" type="application/json">
        {"urlPathname":"/courses","_piniaInitialState":{...},"data":{...}}
      </script>

    Returns:
        The full vike_pageContext dict (keys: urlPathname,
        _piniaInitialState, data, etc.), or None.
    """
    soup = BeautifulSoup(html, "lxml")
    script_tag = soup.find("script", id="vike_pageContext")
    if not script_tag or not script_tag.string:
        return None

    try:
        return json.loads(script_tag.string)
    except json.JSONDecodeError:
        return None


def extract_courses_from_state(page_context: dict) -> List[dict]:
    """Extract course list from the vike_pageContext.

    The courses data is nested at:
      page_context["data"]["courses"]

    where ``data.courses`` = {"totalCount": N, "courses": [...]}.

    Returns:
        List of raw course dicts from the state.
    """
    page_data = page_context.get("data")
    if not isinstance(page_data, dict):
        return []

    courses_container = page_data.get("courses")
    if not isinstance(courses_container, dict):
        return []

    raw_list = courses_container.get("courses", [])
    if not isinstance(raw_list, list):
        return []

    return raw_list


def parse_duration(duration: int, duration_type: int) -> str:
    """Convert duration number and type to human-readable string.

    Duration type mapping:
        1 = lessons/workload (занятия/уроки)
        3 = weeks
        4 = months

    Returns:
        Formatted duration string with Russian pluralization.
    """
    if duration_type == 4:
        # Months
        if 11 <= duration % 100 <= 19:
            return f"{duration} месяцев"
        mod10 = duration % 10
        if mod10 == 1:
            return f"{duration} месяц"
        elif 2 <= mod10 <= 4:
            return f"{duration} месяца"
        else:
            return f"{duration} месяцев"
    elif duration_type == 3:
        # Weeks
        if 11 <= duration % 100 <= 19:
            return f"{duration} недель"
        mod10 = duration % 10
        if mod10 == 1:
            return f"{duration} неделя"
        elif 2 <= mod10 <= 4:
            return f"{duration} недели"
        else:
            return f"{duration} недель"
    elif duration_type == 1:
        # Lessons
        if 11 <= duration % 100 <= 19:
            return f"{duration} занятий"
        mod10 = duration % 10
        if mod10 == 1:
            return f"{duration} занятие"
        elif 2 <= mod10 <= 4:
            return f"{duration} занятия"
        else:
            return f"{duration} занятий"
    else:
        # Unknown type – return raw value
        return f"{duration}"


def format_price(price_kopecks: int) -> str:
    """Format integer price (in roubles) with thousand separators.

    Pikabu stores prices as plain integers representing full rubles.
    Formats as "X XXX ₽" with non-breaking thin space before the currency.
    """
    if price_kopecks <= 0:
        return "Бесплатно"
    return f"{price_kopecks:,} ₽".replace(",", " ")


def parse_start_date(timestamp: int) -> Optional[str]:
    """Convert Unix timestamp to readable date string.

    Args:
        timestamp: Unix timestamp in seconds. 0 means no date.

    Returns:
        Formatted date string like "12 февраля 2024", or None.
    """
    if not timestamp:
        return None

    try:
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        months_ru = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря",
        }
        return f"{dt.day} {months_ru[dt.month]} {dt.year}"
    except (ValueError, OSError):
        return None


def build_course_from_state(raw: dict) -> Dict:
    """Convert a raw course dict from Pinia state to the standard format.

    Args:
        raw: Raw course dict from the SSR state.

    Returns:
        Normalized course dict following the same schema as skillbox/geekbrains parsers.
    """
    school = raw.get("school", {})
    duration_type = raw.get("durationType", 0)
    duration_val = raw.get("duration", 0)

    # Build full price string
    price = raw.get("price", 0)
    price_installment = raw.get("priceInstallment", 0)

    if price_installment:
        price_str = f"от {price_installment:,} ₽/мес".replace(",", " ")
        price_str += f" ({format_price(price)})"
    else:
        price_str = format_price(price)

    # Determine level from title
    title = raw.get("title", "")
    level = infer_level(title)

    # Build the pikabu internal course URL and resolve to actual school page
    pikabu_course_url = urljoin(
        BASE_URL, raw.get("link", {}).get("url", "")
    )
    # Resolve the redirect to get the actual school course page URL
    resolved_course_url = resolve_course_url(pikabu_course_url)

    course = {
        "id": raw.get("id"),
        "title": title.strip(),
        "url": resolved_course_url,  # Use resolved URL as the main course link
        "course_url": resolved_course_url,  # Same as url for consistency
        "school": school.get("title"),
        "school_slug": school.get("slug"),
        "school_url": urljoin(BASE_URL, school.get("url", "")),
        "price": price_str,
        "price_raw": price,
        "price_installment": (
            f"{price_installment:,} ₽/мес".replace(",", " ")
            if price_installment
            else None
        ),
        "rating": raw.get("rating"),
        "review_count": raw.get("reviewCount", 0),
        "duration": parse_duration(duration_val, duration_type),
        "duration_raw": duration_val,
        "duration_type": duration_type,
        "start_date": parse_start_date(raw.get("startDate", 0)),
        "level": level,
        "is_novice_friendly": raw.get("isNoviceFriendly", False),
        "is_hit": raw.get("isHit", False),
        "is_popular": raw.get("isPopular", False),
        "click_count": raw.get("clickCount", 0),
        "source": "pikabu",
    }

    return course


def build_course_from_card(soup_element) -> Optional[Dict]:
    """Parse a single course card from HTML as fallback.

    Extracts data from the rendered card HTML. This is a secondary method
    used when the Pinia state extraction fails or for cross-validation.

    Args:
        soup_element: BeautifulSoup element for a course card.

    Returns:
        Course dict or None if card is invalid.
    """
    # School
    school_elem = soup_element.select_one("a[class*='_school_']")
    school_title_elem = (
        soup_element.select_one("[class*='_school__title_']") if school_elem else None
    )
    school_name = extract_text(school_title_elem) if school_title_elem else None

    # Title
    title_elem = soup_element.select_one("[class*='_title_']")
    title = extract_text(title_elem) if title_elem else ""

    if not title:
        return None

    # Rating – count filled stars
    rating = 0
    filled_stars = soup_element.select(
        "svg[class*='_star_'][class*='_star_filled_']"
    )
    if filled_stars:
        rating = len(filled_stars)

    # Review count
    reviews_elem = soup_element.select_one("[class*='_reviews__link_']")
    review_text = extract_text(reviews_elem) if reviews_elem else ""
    review_count = 0
    if review_text:
        match = re.search(r"(\d+)", review_text)
        if match:
            review_count = int(match.group(1))

    # Duration and start date from the period block
    period_elem = soup_element.select_one("[class*='_period_']")
    duration = None
    start_date = None
    if period_elem:
        # Period contains <div> children – one for each piece of info
        period_parts = period_elem.find_all("div", recursive=False)
        for part in period_parts:
            text = extract_text(part)
            if text:
                if "старт" in text.lower() or "Старт" in text:
                    start_date = text
                elif duration is None:
                    duration = text

    if not duration:
        # Try to get duration from JSON-LD data
        pass

    # Price
    installment_elem = soup_element.select_one("[class*='_priceInstallment_']")
    price_elem = soup_element.select_one("[class*='_price_']:not([class*='_priceInstallment_']):not([class*='_priceDetails_'])")

    installment_text = extract_text(installment_elem) if installment_elem else ""
    price_text = extract_text(price_elem) if price_elem else ""

    if installment_text:
        price_str = f"{installment_text} ({price_text})"
    else:
        price_str = price_text

    # Course link
    link_elem = soup_element.select_one("a[class*='_btnLink_']")
    course_url = None
    if link_elem and link_elem.get("href"):
        course_url = urljoin(BASE_URL, link_elem["href"])
        # Resolve the redirect to get the actual school course page URL
        course_url = resolve_course_url(course_url)

    # School URL / review URL
    reviews_url = None
    if school_elem:
        # The reviews link is separate: a[class*='_reviews__link_']
        rev_link = soup_element.select_one("[class*='_reviews__link_']")
        if rev_link and rev_link.get("href"):
            reviews_url = urljoin(BASE_URL, rev_link["href"])

    level = infer_level(title)

    return {
        "title": title.strip(),
        "url": course_url or reviews_url,
        "course_url": course_url,
        "school": school_name,
        "price": price_str or "Цена не указана",
        "rating": rating,
        "review_count": review_count,
        "duration": duration,
        "start_date": start_date,
        "level": level,
        "source": "pikabu",
    }


def infer_level(title: str) -> Optional[str]:
    """Infer skill level from course title text.

    Mapping rules used by other parsers in this project:
        - beginner: "с нуля", "начальный", "базовый", "junior"
        - advanced: "продвинутый", "advanced", "middle"
        - professional: "профессионал", "pro", "senior", "expert"

    Args:
        title: Course title to analyze.

    Returns:
        Level string or None if undetermined.
    """
    if not title:
        return None

    title_lower = title.lower()

    if any(kw in title_lower for kw in ["с нуля", "начальный", "базовый", "junior"]):
        return "beginner"
    if any(kw in title_lower for kw in ["продвинутый", "advanced", "intermediate", "middle"]):
        return "intermediate"
    if any(kw in title_lower for kw in ["профессионал", "professional", "senior", "expert", "pro"]):
        return "professional"

    return None


def parse_pikabu_courses(url: str = COURSES_URL) -> List[Dict]:
    """Parse courses from Pikabu Courses listing page.

    Primary data source: Pinia SSR state embedded in the page HTML.
    Fallback: rendered HTML card elements.

    The Pinia state contains the first 21 courses sorted by popularity.
    For a more complete listing, additional pages can be loaded via
    category URLs (e.g. /courses-dev, /courses-design).

    Args:
        url: The courses catalog URL. Defaults to the main courses page.

    Returns:
        List of course dictionaries in the standard project format.
    """
    raw_html, soup = fetch_page_raw(url)
    if not raw_html or not soup:
        return []

    courses = []
    seen_ids = set()

    # Strategy 1: Extract from Pinia SSR state (primary – has all fields)
    page_context = extract_page_context(raw_html)
    if page_context:
        raw_courses = extract_courses_from_state(page_context)
        for raw in raw_courses:
            course = build_course_from_state(raw)
            course_id = course.get("id")
            if course_id and course_id not in seen_ids:
                seen_ids.add(course_id)
                courses.append(course)

    # Strategy 2: Fallback to HTML card parsing
    if not courses:
        card_elements = soup.find_all(
            "div", class_=lambda c: c and "_card_" in str(c)
        )

        for card in card_elements:
            course = build_course_from_card(card)
            if course:
                # Deduplicate by course URL
                if course.get("course_url") and course["course_url"] not in seen_ids:
                    seen_ids.add(course["course_url"])
                    courses.append(course)
                elif course.get("url") and course["url"] not in seen_ids:
                    seen_ids.add(course["url"])
                    courses.append(course)

    return courses


def parse_category(category_slug: str) -> List[Dict]:
    """Parse courses from a specific Pikabu category page.

    Args:
        category_slug: Category URL slug (e.g. 'courses-dev', 'courses-design').

    Returns:
        List of course dicts from that category.
    """
    category_url = f"{BASE_URL}/{category_slug}"
    return parse_pikabu_courses(category_url)


def parse_course_detail(course_url: str) -> Optional[Dict]:
    """Parse a single course review/detail page for additional information.

    Pikabu does not host individual course detail pages – the cards link
    directly to external school checkout URLs. This method fetches the
    review page for a course to get additional data.

    Args:
        course_url: Full URL to the course reviews page
                   (e.g. /schools/skillbox/reviews?id=2540).

    Returns:
        Dictionary with course data, or None on failure.
    """
    raw_html, soup = fetch_page_raw(course_url)
    if not raw_html or not soup:
        return None

    # Try to extract from Pinia state first
    page_context = extract_page_context(raw_html)
    if page_context:
        raw_courses = extract_courses_from_state(page_context)
        if raw_courses:
            return build_course_from_state(raw_courses[0])

    # Fallback: extract from review page HTML
    # Title
    title_elem = soup.select_one("h1")
    title = extract_text(title_elem) if title_elem else None

    if not title:
        return None

    course = {
        "title": title,
        "url": course_url,
        "source": "pikabu",
    }

    # Attempt to find school name
    school_elem = soup.select_one("[class*='_school_']")
    if school_elem:
        school_title = school_elem.select_one("[class*='_school__title_']")
        if school_title:
            course["school"] = extract_text(school_title)

    return course


def print_stats(courses: List[Dict]) -> None:
    """Print a summary of parsed course data."""
    if not courses:
        print("No courses found.")
        return

    print(f"\n{'='*80}")
    print(f"  Total courses: {len(courses)}")
    print(f"{'='*80}")
    print()
    for i, c in enumerate(courses, 1):
        print(f"  {i:>2}. {c['title'][:55]:55}")
        print(f"      School:    {c.get('school', 'N/A')}")
        print(f"      Price:     {c.get('price', 'N/A')}")
        print(f"      Rating:    {c.get('rating', 'N/A')} ★ ({c.get('review_count', 0)} отзывов)")
        print(f"      Duration:  {c.get('duration', 'N/A')}")
        print(f"      Level:     {c.get('level', 'N/A')}")
        print(f"      Start:     {c.get('start_date', 'N/A')}")
        print()


if __name__ == "__main__":
    import sys
    import os

    print("Parsing Pikabu Courses...")
    all_courses = parse_pikabu_courses()
    print(f"Found {len(all_courses)} courses")

    # Ask for output path
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = input("Enter path to save JSON file: ").strip()

    if not output_path:
        output_path = "pikabu_courses.json"
        print(f"No path entered, saving to: {output_path}")

    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Write JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_courses)} courses to {output_path}")

    # Stats
    with_price = sum(
        1
        for c in all_courses
        if c.get("price") and c["price"] not in ("Цена не указана", "Бесплатно")
    )
    free = sum(1 for c in all_courses if c.get("price") == "Бесплатно")
    no_price = sum(1 for c in all_courses if c.get("price") == "Цена не указана")

    print(f"  - With price: {with_price}")
    print(f"  - Free: {free}")
    print(f"  - Price not specified: {no_price}")
    print(f"  - With rating: {sum(1 for c in all_courses if c.get('rating'))}")

    if "--stats" in sys.argv:
        print_stats(all_courses)