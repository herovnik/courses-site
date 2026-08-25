"""Parser for GeekBrains (gb.ru) online courses.

Extracts course listings from the API and individual course pages,
normalizing data to the standard Course model.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional
import re
import time
import json

BASE_URL = "https://gb.ru"
API_URL = f"{BASE_URL}/api/v2/courses"
COURSES_URL = f"{BASE_URL}/courses"


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


def fetch_json(url: str, retries: int = 3, delay: float = 1.0) -> Optional[dict | list]:
    """Fetch a URL and return parsed JSON with retry logic.

    Args:
        url: The URL to fetch.
        retries: Number of retry attempts on failure.
        delay: Delay between retries in seconds.

    Returns:
        Parsed JSON data if successful, None otherwise.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} after {retries} attempts: {e}")
                return None
    return None


def extract_text(element) -> str:
    """Safely extract and clean text from a BeautifulSoup element."""
    if element is None:
        return ""
    text = element.get_text(strip=True)
    if not text and element.string:
        text = element.string.strip()
    return text


def parse_duration(text: str) -> Optional[str]:
    """Parse duration string into a normalized format.

    GeekBrains uses formats like "6 месяцев" or "12".
    """
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned if cleaned else None


def parse_price(text: str) -> Optional[str]:
    """Extract price information from text."""
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned if cleaned else None


def parse_level(text: str) -> Optional[str]:
    """Normalize skill level strings."""
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


def extract_price_from_page(soup: BeautifulSoup) -> Optional[str]:
    """Extract price from GeekBrains course page.

    GeekBrains shows prices in format "X XXX₽/мес" inside .price elements.
    """
    import re

    # Price regex patterns - account for zero-width joiners between ₽ and /мес
    patterns = [
        r'[\d\s ]{2,}\s*₽[‍⁠‌]*\s*/\s*мес',
        r'[\d\s ]{4,}\s*₽',
    ]

    def find_price_in_text(text: str, min_price: int = 100) -> Optional[str]:
        """Try each pattern against text, return first match."""
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                price_str = parse_price(m.group())
                if price_str:
                    digits_only = re.sub(r'[^\d]', '', price_str)
                    if digits_only and int(digits_only) >= min_price:
                        return price_str
        return None

    # Strategy 1: Check for free course indicators
    # Check if the H1 mentions "бесплатный"
    title_elem = soup.select_one("h1")
    if title_elem:
        title_text = extract_text(title_elem).lower()
        if "бесплатн" in title_text:
            return "Бесплатно"

    # Check meta description
    meta_desc = soup.select_one("meta[name='description']")
    if meta_desc:
        desc_text = meta_desc.get("content", "").lower()
        if "бесплатный курс" in desc_text or "бесплатно" in desc_text:
            return "Бесплатно"

    # Strategy 2: Direct price element selectors
    price_selectors = [
        ".price__content",
        ".price",
        "[class*='price__']",
        "[class*='price']",
    ]

    for selector in price_selectors:
        elements = soup.select(selector)
        for elem in elements:
            text = extract_text(elem)
            result = find_price_in_text(text)
            if result:
                # Clean up the price - remove zero-width joiners, preserve /мес
                cleaned = result
                for zwj in ['‍', '⁠', '‌']:
                    cleaned = cleaned.replace(zwj, '')
                cleaned = cleaned.strip()
                return cleaned if cleaned else result

    # Strategy 3: Check tags for free courses
    for script in soup.find_all('script'):
        if script.string and 'tags' in script.string and '"free"' in script.string:
            return "Бесплатно"

    # Strategy 4: Search entire page text for price patterns (fallback)
    page_text = extract_text(soup)
    result = find_price_in_text(page_text)
    if result:
        # Check if the price is likely salary info (appears near salary keywords)
        escaped_price = re.escape(result).replace(r'\ ', r'\s*').replace(r'\\ ', r'\s*')
        price_match = re.search(escaped_price, page_text)
        if price_match:
            context_start = max(0, price_match.start() - 100)
            context_end = min(len(page_text), price_match.end() + 100)
            context = page_text[context_start:context_end].lower()
            # Normalize non-standard spaces for keyword matching (NBSP, thin space, etc.)
            context = (context
                .replace('\xa0', ' ')   # non-breaking space
                .replace(' ', ' ')  # thin space
                .replace(' ', ' ')  # narrow no-break space
            )
            salary_keywords = ['зарплат', 'заработк', 'зарабатыва', 'начинающий', 'опытный',
                              'опытные', 'вакансий', 'hh.ru', 'в месяц']
            if any(kw in context for kw in salary_keywords):
                return "Цена не указана"
        cleaned = result
        for zwj in ['‍', '⁠', '‌']:
            cleaned = cleaned.replace(zwj, '')
        # If the result has "/мес" but price is from full page text, try to keep it
        if '/мес' in result and '/мес' not in cleaned:
            pass  # already handled by ZWJ removal above
        cleaned = cleaned.strip()
        return cleaned if cleaned else result

    return "Цена не указана"


def extract_duration_from_text(text: str) -> Optional[str]:
    """Extract duration from page text by scanning for common patterns.

    GeekBrains course pages mention duration in various formats:
    - "8 месяцев обучения"
    - "6 месяцев"
    - "2 недели"
    - "1,5 часа"
    - "160 минут"

    Returns:
        Normalized duration string, or None if no pattern found.
    """
    import re

    # Normalize non-standard spaces
    text = (text
        .replace('\xa0', ' ')   # NBSP
        .replace(' ', ' ')  # thin space
        .replace(' ', ' ')  # narrow no-break space
    )

    def russian_plural(count: int, singular: str, few: str, many: str) -> str:
        """Return correct Russian plural form for a count."""
        if 11 <= count % 100 <= 19:
            return f"{count} {many}"
        mod10 = count % 10
        if mod10 == 1:
            return f"{count} {singular}"
        elif 2 <= mod10 <= 4:
            return f"{count} {few}"
        else:
            return f"{count} {many}"

    # Duration patterns ordered by specificity (most specific first)
    duration_patterns = [
        # "X месяцев" / "X месяца"
        (r'(\d+)\s*месяц(?:ев|а)', lambda m: russian_plural(int(m.group(1)), 'месяц', 'месяца', 'месяцев')),
        # "X,5 месяца"
        (r'(\d)[,.]5\s*месяц(?:а|ев)?', lambda m: f"{m.group(1)},5 месяца"),
        # "X уроков" / "X урока" / "X урок"
        (r'(\d+)\s*урок(?:ов|а)?', lambda m: russian_plural(int(m.group(1)), 'урок', 'урока', 'уроков')),
        # "X занятий" / "X занятия" / "X занятие"
        (r'(\d+)\s*заняти(?:й|я|е)', lambda m: russian_plural(int(m.group(1)), 'занятие', 'занятия', 'занятий')),
        # "X недель" / "X недели" / "X неделя"
        (r'(\d+)\s*недел(?:ь|и|я)', lambda m: russian_plural(int(m.group(1)), 'неделя', 'недели', 'недель')),
        # "X дней" / "X дня"
        (r'(\d+)\s*дн(?:ей|я)', lambda m: russian_plural(int(m.group(1)), 'день', 'дня', 'дней')),
        # "X часов" / "X часа"
        (r'(\d+)\s*час(?:ов|а)?', lambda m: russian_plural(int(m.group(1)), 'час', 'часа', 'часов')),
        # "X,5 часа"
        (r'(\d)[,.]5\s*час(?:ов|а)?', lambda m: f"{m.group(1)},5 часа"),
        # "X минут"
        (r'(\d+)\s*минут(?:ы)?', lambda m: russian_plural(int(m.group(1)), 'минута', 'минуты', 'минут')),
    ]

    best = None
    best_pos = len(text)
    best_is_months = False

    for pattern, formatter in duration_patterns:
        for m in re.finditer(pattern, text.lower()):
            dur_str = formatter(m)
            is_months = 'месяц' in dur_str.lower()

            # Prefer the match that appears earliest in the page
            # But always prefer months over non-months (months are more structured)
            if m.start() < best_pos:
                if is_months or not best_is_months:
                    best = dur_str
                    best_pos = m.start()
                    best_is_months = is_months

    return best


def enrich_from_course_page(course: Dict, soup: BeautifulSoup) -> Dict:
    """Enhance course data by scraping the individual course page."""
    # Description
    desc_elem = (
        soup.select_one("meta[name='description']")
        or soup.select_one(".description")
    )
    if desc_elem:
        if desc_elem.name == "meta":
            course["description"] = desc_elem.get("content", "").strip()
        else:
            course["description"] = extract_text(desc_elem)

    # Price from course page
    if not course.get("price"):
        course["price"] = extract_price_from_page(soup)

    # Duration from course page
    if not course.get("duration"):
        # Strategy 1: Look for duration element by class
        duration_elem = soup.select_one("[class*='duration'], .duration, [class*='term']")
        if duration_elem:
            detailed_duration = parse_duration(extract_text(duration_elem))
            if detailed_duration and ("месяц" in detailed_duration.lower() or "month" in detailed_duration.lower()):
                course["duration"] = detailed_duration

    # Strategy 2: Scan page text for duration patterns
    page_text_for_dur = extract_text(soup)
    if not course.get("duration"):
        dur = extract_duration_from_text(page_text_for_dur)
        if dur:
            course["duration"] = dur

    # Price enhancement: Add "/мес" to prices that should be monthly
    price = course.get("price")
    if price and "₽" in price and "/мес" not in price and "мес" not in price:
        # Check if the course has monthly duration (strong signal)
        dur = course.get("duration", "")
        if dur and "месяц" in dur.lower():
            course["price"] = price.replace("₽", "₽/мес").strip()
        else:
            # Check if page text mentions monthly duration
            normalized_text = page_text_for_dur.replace('\xa0', ' ')
            if re.search(r'\d+\s*месяц', normalized_text.lower()):
                course["price"] = price.replace("₽", "₽/мес").strip()

    # Level from H1 or page content
    if not course.get("level"):
        h1 = soup.select_one("h1")
        if h1:
            title_text = extract_text(h1).lower()
            level = infer_level(title_text)
            if level:
                course["level"] = level

        if not course.get("level"):
            page_text = extract_text(soup).lower()
            level = infer_level(page_text)
            if level:
                course["level"] = level

    return course


def infer_level(text: str) -> Optional[str]:
    """Infer skill level from text content."""
    if "с нуля" in text or "начальный" in text or "базовый" in text or "junior" in text.lower():
        return "beginner"
    elif "продвинутый" in text or "advanced" in text.lower() or "middle" in text.lower():
        return "advanced"
    elif "профессионал" in text or " expert" in text or "senior" in text.lower() or "pro" in text.lower():
        return "professional"
    return None


def parse_geekbrains_courses() -> List[Dict]:
    """Parse all courses from GeekBrains.

    Uses the API to get the list of course URLs, then fetches each
    individual course page to extract accurate title, description,
    price, duration, and level from the actual page.

    Returns:
        List of course dictionaries.
    """
    api_data = fetch_json(API_URL)
    if not api_data:
        return []

    courses = []
    seen_urls = set()

    for item in api_data:
        api_course = item.get("course", item)
        course_path = api_course.get("course_path", "")

        if not course_path:
            continue

        # Build full URL
        course_url = urljoin(BASE_URL, course_path)

        if course_url in seen_urls:
            continue
        seen_urls.add(course_url)

        # Fetch the course page to get accurate data
        course_page = fetch_page(course_url)
        if not course_page:
            continue

        # Extract title from H1
        h1 = course_page.select_one("h1")
        title = extract_text(h1) if h1 else ""

        if not title:
            # Fallback: try meta title or API title
            meta_title = course_page.select_one("meta[property='og:title']")
            if meta_title:
                title = meta_title.get("content", "").strip()
            else:
                title = api_course.get("title", "").strip()

        if not title:
            continue

        # Extract description from meta description
        meta_desc = course_page.select_one("meta[name='description']")
        description = meta_desc.get("content", "").strip() if meta_desc else None

        # Extract price from page
        price = extract_price_from_page(course_page)

        # Extract duration from page
        duration = None
        duration_elem = course_page.select_one("[class*='duration'], .duration, [class*='term']")
        if duration_elem:
            duration = parse_duration(extract_text(duration_elem))

        # If no duration found in specific element, scan page text
        if not duration:
            page_text = extract_text(course_page)
            duration = extract_duration_from_text(page_text)

        # Enhance price: add "/мес" for monthly prices
        if price and price not in ("Бесплатно", "Цена не указана"):
            if "₽" in price and "/мес" not in price and "мес" not in price:
                # Check if duration indicates monthly billing
                if duration and "месяц" in duration.lower():
                    price = price.replace("₽", "₽/мес").strip()
                else:
                    # Check page text for monthly duration mention
                    page_text_check = extract_text(course_page).lower().replace('\xa0', ' ')
                    if re.search(r'\d+\s*месяц', page_text_check):
                        price = price.replace("₽", "₽/мес").strip()

        # Extract level from page
        level = None
        if h1:
            level = infer_level(extract_text(h1).lower())
        if not level:
            page_text = extract_text(course_page).lower()
            level = infer_level(page_text)

        # Check for employment/training info
        employment_status = None
        page_text = extract_text(course_page).lower()
        if any(kw in page_text for kw in ["трудоустройств", "помощь в трудоустройстве", "гарантия трудоустройства", "стажировк"]):
            employment_status = "С помощью в трудоустройстве"

        # Build course dict from actual page data
        course = {
            "title": title,
            "url": course_url,
            "duration": duration,
            "price": price,
            "level": level,
            "employment_status": employment_status,
            "source": "geekbrains",
            "description": description,
        }

        courses.append(course)

    return courses


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
    title_elem = soup.select_one("h1")
    title = extract_text(title_elem)

    if not title:
        return None

    course = {
        "title": title,
        "url": course_url,
        "source": "geekbrains",
    }

    # Enrich with additional details
    course = enrich_from_course_page(course, soup)

    return course


if __name__ == "__main__":
    import sys
    import os

    print("Parsing GeekBrains courses...")
    all_courses = parse_geekbrains_courses()
    print(f"Found {len(all_courses)} courses")

    # Ask for output path
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = input("Enter path to save JSON file: ").strip()

    if not output_path:
        output_path = "geekbrains_courses.json"
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