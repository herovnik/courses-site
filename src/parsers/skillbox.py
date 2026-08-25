"""Parser for Skillbox (skillbox.ru) online courses.

Extracts course listings from the courses catalog page and individual
course pages, normalizing data to the standard Course model.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional
import re
import time
import json

BASE_URL = "https://skillbox.ru"
COURSES_URL = f"{BASE_URL}/courses/"

# CSS selectors based on the observed product-card-new HTML structure
SELECTORS = {
    "course_card": "article.product-card-new",
    "title": ".product-card-new__title",
    "link": ".product-card-new__title",
    "duration": ".product-card-new__feature",
    "employment": ".product-card-new__feature",
    "price": None,  # Not available on listing page
    "level": None,  # Not available on listing page
}

# Fallback selectors for variation in card layouts
FALLBACK_SELECTORS = {
    "title": ["h3", ".card__title", "[data-test='course-title']"],
    "link": ["a", ".card__link"],
    "duration": [".card__duration", ".course-card__meta li:first-child", "[data-test='course-duration']"],
    "employment": [".card__employment", "[data-test='course-employment']"],
    "price": [".card__price", "[data-test='course-price']", ".price"],
    "level": [".card__level", "[data-test='course-level']"],
}


def fetch_page(url: str, retries: int = 3, delay: float = 1.0) -> Optional[BeautifulSoup]:
    """Fetch a page and return parsed HTML with retry logic.

    Args:
        url: The URL to fetch.
        retries: Number of retry attempts on failure.
        delay: Delay between retries in seconds.

    Returns:
        BeautifulSoup object if successful, None otherwise.
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
            return BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} after {retries} attempts: {e}")
                return None
    return None


def extract_text(element) -> str:
    """Safely extract and clean text from a BeautifulSoup element.

    Handles lxml parser quirk where get_text() returns empty for single
    text nodes but .string property works correctly.
    """
    if element is None:
        return ""
    text = element.get_text(strip=True)
    # Fallback: lxml parser sometimes returns empty get_text() for single text nodes
    if not text and element.string:
        text = element.string.strip()
    return text


def parse_duration(text: str) -> Optional[str]:
    """Parse duration string into a normalized format.

    Skillbox uses formats like "10 месяцев" or "6 months".
    Returns the raw text if parsing is inconclusive.
    """
    if not text:
        return None
    # Remove extra whitespace
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned if cleaned else None


def parse_price(text: str) -> Optional[str]:
    """Extract price information from text.

    Skillbox may show "от 50 000 ₽" or "Бесплатно".
    """
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned if cleaned else None


def parse_level(text: str) -> Optional[str]:
    """Normalize skill level strings.

    Maps variations like 'начальный', 'с нуля', 'базовый' to 'beginner',
    'продвинутый' to 'advanced', etc.
    """
    if not text:
        return None

    level_map = {
        "начальный": "beginner",
        "с нуля": "beginner",
        "базовый": "beginner",
        "продвинутый": "advanced",
        "средний": "intermediate",
        "профессиональная": "professional",
    }

    normalized = text.lower().strip()
    for key, value in level_map.items():
        if key in normalized:
            return value
    return normalized


def get_element_with_fallback(soup, selector, fallback_list=None):
    """Try primary selector, then fall back to alternatives."""
    element = soup.select_one(selector)
    if element:
        return element

    if fallback_list:
        for fallback in fallback_list:
            element = soup.select_one(fallback)
            if element:
                return element
    return None


def parse_course_card(card) -> Optional[Dict]:
    """Parse a single course card element into a Course dict.

    Args:
        card: BeautifulSoup element representing a course card.

    Returns:
        Dictionary with course data, or None if required fields are missing.
    """
    # Extract title
    title_elem = get_element_with_fallback(
        card, SELECTORS["title"], FALLBACK_SELECTORS["title"]
    )
    title = extract_text(title_elem)

    if not title:
        return None

    # Extract link
    link_elem = card.select_one(SELECTORS["link"]) or card.find("a")
    link = None
    if link_elem and link_elem.get("href"):
        link = urljoin(BASE_URL, link_elem["href"])

    # Extract features (duration, employment status, etc.)
    features = card.select(SELECTORS["duration"])
    duration = None
    employment = None

    for feat in features:
        text = extract_text(feat)
        if "месяц" in text.lower() or "month" in text.lower():
            duration = parse_duration(text)
        elif "трудоустройств" in text.lower() or "employment" in text.lower() or "работ" in text.lower():
            employment = text

    # Extract price (not on listing page)
    price = None

    # Extract level (not on listing page, but can infer from title)
    level = None
    title_lower = title.lower()
    if "с нуля" in title_lower or "начальный" in title_lower or "базовый" in title_lower:
        level = "beginner"
    elif "продвинутый" in title_lower or "advanced" in title_lower:
        level = "advanced"
    elif "профессионал" in title_lower or "pro" in title_lower:
        level = "professional"

    # Build course dict
    course = {
        "title": title,
        "url": link,
        "duration": duration,
        "price": price,
        "level": level,
        "employment_status": employment,
        "source": "skillbox",
    }

    # If we have a link, fetch the course page for additional details
    if link:
        course_page = fetch_page(link)
        if course_page:
            course = enrich_from_course_page(course, course_page)

    return course


def enrich_from_course_page(course: Dict, soup: BeautifulSoup) -> Dict:
    """Enhance course data by scraping the individual course page.

    Extracts more detailed info like full description, curriculum,
    and instructor details when available. Preserves card-level fields.
    """
    # Description
    desc_elem = (
        soup.select_one(".course-header__description")
        or soup.select_one(".description")
        or soup.select_one("meta[name='description']")
    )
    if desc_elem:
        if desc_elem.name == "meta":
            course["description"] = desc_elem.get("content", "").strip()
        else:
            course["description"] = extract_text(desc_elem)

    # Price from course page - try multiple selectors for different page layouts
    if not course.get("price"):
        course["price"] = extract_price_from_page(soup)

    # Duration from course page
    if not course.get("duration"):
        # Look for duration in spoiler subtitles or similar
        duration_elem = soup.select_one(".ui-spoiler__subtitle-text, .course-header__duration, .duration")
        if duration_elem:
            detailed_duration = parse_duration(extract_text(duration_elem))
            if detailed_duration and ("месяц" in detailed_duration.lower() or "month" in detailed_duration.lower()):
                course["duration"] = detailed_duration

    # Level from course page (infer from content)
    if not course.get("level"):
        # Check for level indicators in the page
        page_text = extract_text(soup).lower()
        if "с нуля" in page_text or "начальный" in page_text or "базовый" in page_text:
            course["level"] = "beginner"
        elif "продвинутый" in page_text or "advanced" in page_text:
            course["level"] = "advanced"
        elif "профессионал" in page_text or " эксперт" in page_text:
            course["level"] = "professional"

    # Employment status from course page
    if not course.get("employment_status"):
        # Look for employment guarantee text
        employment_elem = soup.select_one(".work-v6__refund-text, .start-screen-v3__utp-title, .price-v9__features")
        if employment_elem:
            text = extract_text(employment_elem)
            if "трудоустройств" in text.lower() or "работ" in text.lower() and "найти" in text.lower():
                course["employment_status"] = text[:200]  # Limit length

    return course


def extract_price_from_page(soup: BeautifulSoup) -> Optional[str]:
    """Extract price from course page using multiple strategies.

    Handles different page layouts: price-v8, price-v9, price-v10,
    free courses, online college courses, and multi-tier pricing.
    All prices are extracted from specific elements, not from the full
    page text, to avoid false positives from navigation and footer text.
    """
    import re

    # Price regex patterns - ordered by specificity (most specific first)
    patterns = [
        # Per-month or per-lesson price (most specific)
        r'[\d\s ]{2,}\s*₽/\s*мес',
        r'[\d\s ]{2,}\s*₽/урок',
        # Price with "от" prefix and per-lesson/monthly suffix
        r'от\s*[\d\s ]+\s*₽/\s*(?:мес|урок)',
        # Any price with at least 4 digits (filters out 99₽ trial lessons)
        r'[\d\s ]{4,}\s*₽',
    ]

    def is_course_free(soup: BeautifulSoup) -> bool:
        """Check if the course is free by examining title and meta description."""
        # Check if the H1 explicitly mentions "бесплатный" course
        title_elem = soup.select_one("h1") or soup.select_one(".course-header__title")
        if title_elem:
            title_text = extract_text(title_elem).lower()
            # Check for any form of "бесплатно" in the title
            if "бесплатн" in title_text:
                return True

        # Check meta description
        meta_desc = soup.select_one("meta[name='description']")
        if meta_desc:
            desc_text = meta_desc.get("content", "").lower()
            if "бесплатный курс" in desc_text or "бесплатно" in desc_text:
                return True

        # Check for explicit "0₽" in price-related elements
        for elem in soup.find_all(class_=re.compile(r'price|cost', re.I)):
            text = extract_text(elem)
            if re.search(r'0\s*₽', text) and len(text) < 200:
                return True

        return False

    # Check for free course indicators BEFORE any price extraction
    # If the title explicitly says "бесплатный", return immediately
    if is_course_free(soup):
        return "Бесплатно"

    def find_price_in_text(text: str, min_price: int = 100) -> Optional[str]:
        """Try each pattern against text, return first match.

        Args:
            text: Text to search for price patterns.
            min_price: Minimum price value to consider valid (filters out
                      trial lesson prices like 99₽).
        """
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                price_str = parse_price(m.group())
                if price_str:
                    # Remove all non-digit characters to get numeric value
                    # (handles regular spaces, thin spaces U+2009, etc.)
                    digits_only = re.sub(r'[^\d]', '', price_str)
                    if digits_only and int(digits_only) >= min_price:
                        return price_str
        return None

    # Strategy 1: Direct price element selectors (most reliable)
    price_selectors = [
        ".price-v8__content",
        ".price-v8__price",
        ".price-v9__primary-price",
        ".price-v9__price",
        ".price-v10__price",
        ".price-v10__price-count",
        ".price-v10__amount",
        ".price-info__price",
        ".price-info__item",
        ".price-info__list",
        ".tariffs-v5__price .tariffs-v5__price-value",
        ".tariffs__price-value",
        ".price__value",
        ".course-price__value",
        ".ui-autopayment-method__images",
    ]

    for selector in price_selectors:
        elements = soup.select(selector)
        for elem in elements:
            text = extract_text(elem)
            result = find_price_in_text(text)
            if result and not result.lower().startswith("бесплатно"):
                return result

    # Strategy 2: Look for price in any element with price-related class
    for elem in soup.find_all(class_=re.compile(r'price|cost|tariff|pay|payment', re.I)):
        text = extract_text(elem)
        if len(text) > 500:
            continue
        result = find_price_in_text(text)
        if result:
            return result

    # Strategy 3: Online college (spo-*) courses - look for "X рублей в месяц" pattern
    for elem in soup.find_all(['div', 'p', 'span']):
        text = extract_text(elem)
        if len(text) > 500:
            continue
        # Use a pattern that captures the full number including thin spaces
        college_match = re.search(r'([\d\s ]+руб(?:ля|лей)?\s*в\s*месяц)', text, re.IGNORECASE)
        if college_match:
            full_price = college_match.group(1)
            # Skip if context contains salary-related keywords
            context_lower = text.lower()
            if any(kw in context_lower for kw in ['зарплат', 'заработк', 'вакансий', 'hh.ru']):
                continue
            # Extract just the digits from the price part
            price_match = re.search(r'[\d\s ]{2,}', full_price)
            if price_match:
                price_val = parse_price(price_match.group())
                if price_val and int(price_val.replace(' ', '').replace(' ', '')) <= 1000:
                    return f"{price_val} руб/мес"

    # Strategy 5: Search entire page text for price patterns (fallback)
    # Skip salary-related text to avoid extracting salary info as course price
    main_content = soup.select_one("main, .content, .page-content, .course-page, .container")
    if main_content:
        page_text = extract_text(main_content)
    else:
        page_text = extract_text(soup)

    result = find_price_in_text(page_text)
    if result:
        # Check if the price is likely salary info (appears near salary keywords)
        # Use regex to find the price in text (handles thin spaces, etc.)
        escaped_price = re.escape(result).replace(r'\ ', r'\s*').replace(r'\\ ', r'\s*')
        price_match = re.search(escaped_price, page_text)
        if price_match:
            context_start = max(0, price_match.start() - 100)
            context_end = min(len(page_text), price_match.end() + 100)
            context = page_text[context_start:context_end].lower()
            # Normalize non-standard spaces for keyword matching (NBSP, thin space, etc.)
            context = (context
                .replace('\xa0', ' ')   # non-breaking space
                .replace(' ', ' ') # thin space
                .replace(' ', ' ') # narrow no-break space
            )
            # Skip if context contains salary-related keywords
            salary_keywords = ['зарплат', 'заработк', 'зарабатыва', 'начинающий', 'опытный',
                              'опытные', 'вакансий', 'hh.ru', 'после обучения']
            if any(kw in context for kw in salary_keywords):
                return "Цена не указана"
        return result

    # No price found at all - mark as "Цена не указана"
    return "Цена не указана"


def parse_skillbox_courses(url: str = COURSES_URL) -> List[Dict]:
    """Parse all courses from the Skillbox courses listing page.

    Args:
        url: The courses catalog URL. Defaults to the main courses page.

    Returns:
        List of course dictionaries.
    """
    soup = fetch_page(url)
    if not soup:
        return []

    courses = []
    seen_urls = set()

    # Primary selector for course cards
    course_cards = soup.select(SELECTORS["course_card"])

    # Fallback: look for any anchor tags with course-like structure
    if not course_cards:
        course_cards = soup.select(".card__body, .product-card, [data-test='course-card']")

    for card in course_cards:
        course = parse_course_card(card)
        if course and course["url"]:
            # Deduplicate by URL
            if course["url"] not in seen_urls:
                seen_urls.add(course["url"])
                courses.append(course)
        elif course:
            # Include courses without URLs (unlikely but possible)
            courses.append(course)

    # If no structured cards found, try scraping individual course links
    if not courses:
        course_links = soup.select("a[href*='/course/']")
        for link in course_links:
            href = link.get("href")
            if href:
                full_url = urljoin(BASE_URL, href)
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    page_soup = fetch_page(full_url)
                    if page_soup:
                        title_elem = (
                            page_soup.select_one("h1")
                            or page_soup.select_one(".course-title")
                            or page_soup.select_one(".header__title")
                        )
                        course = {
                            "title": extract_text(title_elem) if title_elem else "Untitled",
                            "url": full_url,
                            "source": "skillbox",
                        }
                        course = enrich_from_course_page(course, page_soup)
                        courses.append(course)

    return courses


def parse_category(category_slug: str) -> List[Dict]:
    """Parse courses from a specific Skillbox category (e.g., 'code', 'design').

    Args:
        category_slug: The category identifier from the URL path.

    Returns:
        List of course dictionaries from that category.
    """
    category_url = f"{BASE_URL}/courses/{category_slug}/"
    return parse_skillbox_courses(category_url)


def parse_course_detail(course_url: str) -> Optional[Dict]:
    """Parse a single course page for detailed information.

    Args:
        course_url: Full URL to the individual course page.

    Returns:
        Dictionary with detailed course data, or None on failure.
    """
    soup = fetch_page(course_url)
    if not soup:
        return None

    # Title
    title_elem = (
        soup.select_one("h1.course-header__title")
        or soup.select_one("h1")
        or soup.select_one(".page-title")
    )
    title = extract_text(title_elem)

    if not title:
        return None

    course = {
        "title": title,
        "url": course_url,
        "source": "skillbox",
    }

    # Enrich with additional details
    course = enrich_from_course_page(course, soup)

    return course


if __name__ == "__main__":
    import sys
    import os

    print("Parsing Skillbox courses...")
    all_courses = parse_skillbox_courses()
    print(f"Found {len(all_courses)} courses")

    # Ask for output path
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = input("Enter path to save JSON file: ").strip()

    if not output_path:
        output_path = "skillbox_courses.json"
        print(f"No path entered, saving to: {output_path}")

    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Write JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_courses)} courses to {output_path}")
    print(f"  - With price: {sum(1 for c in all_courses if c.get('price') and c['price'] not in ('Цена не указана', 'Бесплатно'))}")
    print(f"  - Free: {sum(1 for c in all_courses if c.get('price') == 'Бесплатно')}")
    print(f"  - Price not specified: {sum(1 for c in all_courses if c.get('price') == 'Цена не указана')}")
