#!/usr/bin/env python3
"""Convert parser JSON outputs to frontend Course type format."""

import json
import re
from typing import List, Dict, Any, Optional

# School mapping for display names and logos
SCHOOL_CONFIG = {
    "skillbox": {"name": "Skillbox", "logo": "SB"},
    "geekbrains": {"name": "GeekBrains", "logo": "GB"},
    "pikabu": {"name": "", "logo": ""},  # Will use school field from pikabu
}

# Category mapping based on course title/keywords
CATEGORY_KEYWORDS = {
    "Программирование": [
        "разработчик", "программист", "python", "java", "frontend", "backend",
        "fullstack", "unity", "unreal", "геймдев", "игры", "тестировани", "qa",
        "кибербезопас", "devops", "1c", "1с", "мобильные", "android", "ios",
        "flutter", "react", "vue", "angular", "node", "go", "rust", "c++", "c#",
        ".net", "php", "javascript", "typescript", "sql", "базы данных",
        "алгоритмы", "структуры данных", "computer science", "архитектура",
        "микросервисы", "docker", "kubernetes", "linux", "git", "api",
        "machine learning", "ml", "data science", "нейросети", "ии", "ai",
        "оператор", "мультипликатор", "режиссёр", "монтаж", "съёмк",
        "битмейк", "музыка", "продюсер", "сонграйтер", "электронная музыка",
        "фитнес", "спорт", "тренер",
    ],
    "Дизайн": [
        "дизайнер", "3d-художник", "2d-художник", "концепт-художник",
        "геймдизайнер", "3d-дженералист", "3d-женералист", "ux/ui", "ui/ux",
        "веб-дизайнер", "графический", "иллюстратор", "интерьер", "ландшафт",
        "аниматор", "концепт-арт", "концепт арт", "персонажи", "моделирование",
        "blender", "maya", "zbrush", "substance", "houdini", "figma", "photoshop",
        "illustrator", "инфографика", "маркетплейс",
    ],
    "Маркетинг": [
        "маркетолог", "smm", "таргетолог", "контекстная", "seo", "копирайтер",
        "контент-маркетолог", "email-маркетолог", "продакшн", "автофаннел",
        "воронка", "лидогенерация", "аналитика маркетинга", "бренд", "pr",
        "пиар", "социальные сети", "инстаграм", "вконтакте", "телеграм",
        "youtube", "тикtok", "реклама", "продвижение", "ai-креатор", "нейросети",
    ],
    "Менеджмент": [
        "менеджер", "project manager", "проджект-менеджер", "продакт-менеджер",
        "product manager", "product owner", "hr", "рекрутер", "кадры",
        "event-менеджер", "ивент-менеджер", "маркетплейс", "wb", "ozon",
        "селлер", "авито", "avito", "менеджмент", "управление проектами",
        "agile", "scrum", "kanban", "jira", "управление продуктом",
    ],
    "Аналитика": [
        "аналитик", "data analyst", "бизнес-аналитик", "business analyst",
        "системный аналитик", "финансовый аналитик", "продуктовый аналитик",
        "marketing analyst", "данные", "sql", "tableau", "power bi", "python анализ",
        "machine learning анализ", "статистика", "a/b тест", "метрики",
    ],
    "Финансы": [
        "бухгалтер", "финансист", "экономист", "налог", "1с:бухгалтерия",
        "финмодел", "кредитный", "инвестиционный", "банковский", "аудит",
        "налоговое консультирование", "юрист", "правовед",
    ],
}

LEVEL_MAP = {
    "beginner": "Начинающий",
    "intermediate": "Средний",
    "advanced": "Продвинутый",
    "professional": "Продвинутый",
}

def parse_price(price_str: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    """Parse price string to (monthly_price, old_monthly_price).

    Returns (price, old_price) where both are in rubles per month.
    """
    if not price_str:
        return None, None

    price_str = price_str.strip()

    # Free course
    if "бесплатно" in price_str.lower() or "бесплатн" in price_str.lower():
        return 0, None

    # Price not specified
    if "цена не указана" in price_str.lower():
        return None, None

    # Pikabu format: "от 8 500 ₽/мес (87 000 ₽)"
    installment_match = re.search(r'от\s*([\d\s]+)\s*₽\s*/\s*мес\s*\(([\d\s]+)\s*₽\)', price_str)
    if installment_match:
        monthly = int(installment_match.group(1).replace(" ", ""))
        total = int(installment_match.group(2).replace(" ", ""))
        # Calculate old monthly price from total (assuming 12 months typical)
        old_monthly = total // 12 if total > 0 else None
        return monthly, old_monthly

    # Pikabu format: "19 500 ₽" (one-time price)
    onetime_match = re.search(r'^([\d\s]+)\s*₽$', price_str)
    if onetime_match:
        total = int(onetime_match.group(1).replace(" ", ""))
        # Convert to monthly assuming 12 months
        monthly = total // 12
        return monthly, None

    # Standard format: "6 921₽/мес" or "6 921 ₽/мес"
    monthly_match = re.search(r'([\d\s]+)\s*₽\s*/\s*мес', price_str)
    if monthly_match:
        monthly = int(monthly_match.group(1).replace(" ", ""))
        return monthly, None

    # Format with "от": "от 5 000 ₽/мес"
    from_match = re.search(r'от\s*([\d\s]+)\s*₽\s*/\s*мес', price_str)
    if from_match:
        monthly = int(from_match.group(1).replace(" ", ""))
        return monthly, None

    # Try to find any number with ₽
    any_price = re.search(r'([\d\s]+)\s*₽', price_str)
    if any_price:
        val = int(any_price.group(1).replace(" ", ""))
        # Heuristic: if > 50000, it's likely total price, convert to monthly
        if val > 50000:
            return val // 12, None
        return val, None

    return None, None


def parse_duration(duration_str: Optional[str]) -> int:
    """Parse duration string to months (int)."""
    if not duration_str:
        return 12  # default

    duration_str = duration_str.lower().strip()

    # Months: "13 месяцев", "10 месяцев", "2 месяца"
    month_match = re.search(r'(\d+(?:[.,]\d+)?)\s*месяц', duration_str)
    if month_match:
        return int(float(month_match.group(1).replace(",", ".")))

    # Weeks: "5 недель" -> ~1.25 months
    week_match = re.search(r'(\d+)\s*недел', duration_str)
    if week_match:
        weeks = int(week_match.group(1))
        return max(1, round(weeks / 4.33))

    # Lessons: "60 занятий" - can't convert reliably, assume 3-4 months
    lesson_match = re.search(r'(\d+)\s*занят', duration_str)
    if lesson_match:
        lessons = int(lesson_match.group(1))
        return max(1, round(lessons / 8))  # ~2 lessons/week

    # Hours: "160 минут" etc.
    hour_match = re.search(r'(\d+(?:[.,]\d+)?)\s*час', duration_str)
    if hour_match:
        hours = float(hour_match.group(1).replace(",", "."))
        return max(1, round(hours / 40))  # ~40 hours/month

    # Days
    day_match = re.search(r'(\d+)\s*дн', duration_str)
    if day_match:
        days = int(day_match.group(1))
        return max(1, round(days / 30))

    return 12  # default


def infer_category(title: str, description: str = "") -> str:
    """Infer category from title and description."""
    text = (title + " " + description).lower()

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)

    return "Программирование"  # default


def infer_level(level_str: Optional[str]) -> str:
    """Map parser level to frontend level."""
    if not level_str:
        return "Начинающий"
    return LEVEL_MAP.get(level_str.lower(), "Начинающий")


def get_school_info(source: str, course: Dict) -> tuple[str, str]:
    """Get school name and logo."""
    if source == "pikabu":
        school = course.get("school", "Неизвестно")
        # Short logo from school name
        logo = "".join(w[0] for w in school.split()[:2]).upper()[:2]
        return school, logo

    config = SCHOOL_CONFIG.get(source, {"name": source.capitalize(), "logo": source[:2].upper()})
    return config["name"], config["logo"]


def clean_description(desc: Optional[str]) -> str:
    """Clean and truncate description."""
    if not desc:
        return "Описание отсутствует"
    # Remove emoji and special chars, truncate
    desc = re.sub(r'[⚡🍋⭐✅🧑‍🎓🔥✨]', '', desc)
    desc = re.sub(r'\s+', ' ', desc).strip()
    return desc[:200] + ("..." if len(desc) > 200 else "")


def generate_tags(title: str, category: str, source: str) -> List[str]:
    """Generate tags from title and category."""
    tags = [category]
    title_lower = title.lower()

    tag_keywords = {
        "Python": ["python", "питон"],
        "Java": ["java", "джава"],
        "JavaScript": ["javascript", "js ", "typescript", "ts "],
        "React": ["react"],
        "Vue": ["vue"],
        "Unity": ["unity"],
        "Unreal Engine": ["unreal", "ue5"],
        "C++": ["c++", "cpp"],
        "Go": ["golang", " go "],
        "Rust": ["rust"],
        "SQL": ["sql", "базы данных"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "ML": ["machine learning", "ml ", "нейросет", "ии ", "ai "],
        "Data Science": ["data science", "аналитик данных"],
        "DevOps": ["devops"],
        "QA": ["тестировани", "qa "],
        "Cybersecurity": ["кибербезопас", "информационная безопас"],
        "Figma": ["figma"],
        "Photoshop": ["photoshop"],
        "Blender": ["blender"],
        "Unity": ["unity"],
        "3D": ["3d", "трехмерн"],
        "UX/UI": ["ux/ui", "ui/ux", "юзабилити"],
        "SMM": ["smm", "социальные сети"],
        "SEO": ["seo"],
        "Copywriting": ["копирайтер", "копирайтинг"],
        "Project Management": ["проектн", "менеджер проект"],
        "Product Management": ["продукт", "product"],
        "HR": [" hr ", "рекрутер", "кадров"],
        "English": ["english", "английск"],
    }

    for tag, keywords in tag_keywords.items():
        if any(kw in title_lower for kw in keywords):
            tags.append(tag)

    # Limit tags
    return tags[:5]


def convert_course(course: Dict, idx: int) -> Dict:
    """Convert a single parser course to frontend format."""
    source = course.get("source", "unknown")
    title = course.get("title", f"Course {idx}")
    url = course.get("url") or course.get("course_url", "")
    duration_str = course.get("duration", "")
    price_str = course.get("price", "")
    level_str = course.get("level", "")
    description = course.get("description", "")
    employment = course.get("employment_status", "")
    rating = course.get("rating")
    review_count = course.get("review_count", 0)

    # Parse price
    price, old_price = parse_price(price_str)

    # If no price found, set to None (will be filtered out or shown as "Цена не указана")
    if price is None:
        price = 0
        has_price = False
    else:
        has_price = True

    # Parse duration
    duration = parse_duration(duration_str)

    # Infer category
    category = infer_category(title, description)

    # Infer level
    level = infer_level(level_str)

    # School info
    school, school_logo = get_school_info(source, course)

    # Clean description
    clean_desc = clean_description(description)

    # Generate tags
    tags = generate_tags(title, category, source)

    # Determine if hot/new based on various signals
    is_hot = False
    is_new = False
    if source == "pikabu":
        is_hot = course.get("is_hit", False)
        is_new = course.get("is_popular", False)
    elif employment and "трудоустройств" in employment.lower():
        is_hot = True

    # Certificate - assume true for paid courses with employment
    certificate = has_price and (employment is not None or price > 0)

    # Rating and reviews
    if rating is not None:
        rating_val = float(rating)
        reviews = int(review_count) if review_count else 0
    else:
        # Default rating based on source
        rating_val = 4.5 if source in ["skillbox", "geekbrains"] else 4.0
        reviews = 0

    # Students count - estimate from click_count for pikabu, or default
    if source == "pikabu":
        students = course.get("click_count", 100)
    else:
        students = 100  # default

    # Image placeholder based on category
    category_images = {
        "Программирование": "https://images.pexels.com/photos/574077/pexels-photo-574077.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Дизайн": "https://images.pexels.com/photos/5649518/pexels-photo-5649518.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Маркетинг": "https://images.pexels.com/photos/5912284/pexels-photo-5912284.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Менеджмент": "https://images.pexels.com/photos/6326370/pexels-photo-6326370.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Аналитика": "https://images.pexels.com/photos/5912280/pexels-photo-5912280.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Финансы": "https://images.pexels.com/photos/4497757/pexels-photo-4497757.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
    }
    image = category_images.get(category, category_images["Программирование"])

    return {
        "id": idx,
        "title": title,
        "school": school,
        "schoolLogo": school_logo,
        "category": category,
        "description": clean_desc,
        "price": price,
        "oldPrice": old_price,
        "duration": duration,
        "level": level,
        "rating": rating_val,
        "reviewsCount": reviews,
        "studentsCount": students,
        "image": image,
        "tags": tags,
        "isHot": is_hot,
        "isNew": is_new,
        "certificate": certificate,
        "url": url,
    }


def main():
    # Load parser outputs
    all_courses = []

    for parser_file, source_name in [
        ("/home/nikon/test/edu/site-agregator/skillbox_courses.json", "skillbox"),
        ("/home/nikon/test/edu/site-agregator/geekbrains_courses.json", "geekbrains"),
        ("/home/nikon/test/edu/site-agregator/pikabu_courses.json", "pikabu"),
    ]:
        try:
            with open(parser_file, "r", encoding="utf-8") as f:
                courses = json.load(f)

            for i, course in enumerate(courses):
                course["source"] = source_name
                all_courses.append(course)
        except FileNotFoundError:
            print(f"Warning: {parser_file} not found")
        except json.JSONDecodeError as e:
            print(f"Error parsing {parser_file}: {e}")

    print(f"Total raw courses: {len(all_courses)}")

    # Convert to frontend format
    frontend_courses = []
    for idx, course in enumerate(all_courses, 1):
        try:
            converted = convert_course(course, idx)
            # Only include courses with valid titles and URLs
            if converted["title"] and converted["url"]:
                frontend_courses.append(converted)
        except Exception as e:
            print(f"Error converting course {course.get('title', 'unknown')}: {e}")

    print(f"Converted courses: {len(frontend_courses)}")

    # Stats
    free_count = sum(1 for c in frontend_courses if c["price"] == 0)
    paid_count = sum(1 for c in frontend_courses if c["price"] > 0)
    no_price = sum(1 for c in frontend_courses if c["price"] is None)
    print(f"Free: {free_count}, Paid: {paid_count}, No price: {no_price}")

    # Categories
    cats = {}
    for c in frontend_courses:
        cats[c["category"]] = cats.get(c["category"], 0) + 1
    print("Categories:", cats)

    # Schools
    schools = {}
    for c in frontend_courses:
        schools[c["school"]] = schools.get(c["school"], 0) + 1
    print("Schools:", schools)

    # Generate TypeScript file
    ts_content = generate_ts(frontend_courses)

    output_path = "/home/nikon/test/edu/site-agregator/site/src/data/courses.ts"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ts_content)

    print(f"\nWritten to {output_path}")


def generate_ts(courses: List[Dict]) -> str:
    """Generate TypeScript file content."""
    lines = []
    lines.append("export type Course = {")
    lines.append("  id: number;")
    lines.append("  title: string;")
    lines.append("  school: string;")
    lines.append("  schoolLogo: string;")
    lines.append("  category: string;")
    lines.append("  description: string;")
    lines.append("  price: number;")
    lines.append("  oldPrice?: number;")
    lines.append("  duration: number; // months")
    lines.append('  level: "Начинающий" | "Средний" | "Продвинутый";')
    lines.append("  rating: number;")
    lines.append("  reviewsCount: number;")
    lines.append("  studentsCount: number;")
    lines.append("  image: string;")
    lines.append("  tags: string[];")
    lines.append("  isHot?: boolean;")
    lines.append("  isNew?: boolean;")
    lines.append("  certificate: boolean;")
    lines.append("  url: string;  // Link to the actual course page")
    lines.append("};")
    lines.append("")

    # Schools list
    schools = sorted(set(c["school"] for c in courses))
    lines.append("export const schools = [")
    for s in schools:
        lines.append(f'  "{s}",')
    lines.append("];")
    lines.append("")

    # Categories list
    categories = sorted(set(c["category"] for c in courses))
    lines.append("export const categories = [")
    lines.append('  "Все",')
    for c in categories:
        lines.append(f'  "{c}",')
    lines.append("];")
    lines.append("")

    # Courses array
    lines.append("export const courses: Course[] = [")
    for c in courses:
        lines.append("  {")
        lines.append(f'    id: {c["id"]},')
        lines.append(f'    title: "{escape_ts(c["title"])}",')
        lines.append(f'    school: "{escape_ts(c["school"])}",')
        lines.append(f'    schoolLogo: "{c["schoolLogo"]}",')
        lines.append(f'    category: "{c["category"]}",')
        lines.append(f'    description: "{escape_ts(c["description"])}",')
        lines.append(f'    price: {c["price"]},')
        if c["oldPrice"] is not None:
            lines.append(f'    oldPrice: {c["oldPrice"]},')
        lines.append(f'    duration: {c["duration"]},')
        lines.append(f'    level: "{c["level"]}",')
        lines.append(f'    rating: {c["rating"]},')
        lines.append(f'    reviewsCount: {c["reviewsCount"]},')
        lines.append(f'    studentsCount: {c["studentsCount"]},')
        lines.append(f'    image: "{c["image"]}",')
        lines.append(f'    tags: {json.dumps(c["tags"], ensure_ascii=False)},')
        if c["isHot"]:
            lines.append(f'    isHot: true,')
        if c["isNew"]:
            lines.append(f'    isNew: true,')
        lines.append(f'    certificate: {str(c["certificate"]).lower()},')
        lines.append(f'    url: "{c["url"]}",')
        lines.append("  },")
    lines.append("];")
    lines.append("")

    return "\n".join(lines)


def escape_ts(s: str) -> str:
    """Escape string for TypeScript."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")


if __name__ == "__main__":
    main()