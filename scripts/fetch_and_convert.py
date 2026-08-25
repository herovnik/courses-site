#!/usr/bin/env python3
"""
Fetch courses from all parsers and convert to TypeScript format for the site.
"""

import sys
import os
import json
import re

# Add src to path
sys.path.insert(0, '/home/nikon/test/edu/site-agregator/src')

from parsers.skillbox import parse_skillbox_courses
from parsers.geekbrains import parse_geekbrains_courses
from parsers.pikabu import parse_pikabu_courses


def parse_price_to_number(price_str: str) -> int:
    """Convert price string to monthly price in rubles (number)."""
    if not price_str or price_str in ("Цена не указана", "Бесплатно"):
        return 0

    # Extract numbers from strings like "6 921₽/мес", "от 8 500 ₽/мес (87 000 ₽)", "19 500 ₽"
    # Look for monthly price first (contains /мес)
    monthly_match = re.search(r'от\s*([\d\s]+)\s*₽\s*/\s*мес', price_str)
    if monthly_match:
        return int(monthly_match.group(1).replace(' ', ''))

    monthly_match2 = re.search(r'([\d\s]+)\s*₽\s*/\s*мес', price_str)
    if monthly_match2:
        return int(monthly_match2.group(1).replace(' ', ''))

    # Look for full price in parentheses
    full_price_match = re.search(r'\(([\d\s]+)\s*₽\)', price_str)
    if full_price_match:
        full_price = int(full_price_match.group(1).replace(' ', ''))
        # Estimate monthly (assume 12 months)
        return full_price // 12

    # Just a plain price like "19 500 ₽" or "3000 ₽"
    plain_match = re.search(r'([\d\s]+)\s*₽', price_str)
    if plain_match:
        return int(plain_match.group(1).replace(' ', ''))

    return 0


def parse_duration_to_months(duration_str: str) -> int:
    """Convert duration string to months (number)."""
    if not duration_str:
        return 1

    duration_str = duration_str.lower()

    # Months
    month_match = re.search(r'(\d+[,.]?\d*)\s*месяц', duration_str)
    if month_match:
        return int(float(month_match.group(1).replace(',', '.')))

    # Weeks - convert to months (4 weeks = 1 month)
    week_match = re.search(r'(\d+)\s*недел', duration_str)
    if week_match:
        weeks = int(week_match.group(1))
        return max(1, weeks // 4)

    # Days - convert to months (30 days = 1 month)
    day_match = re.search(r'(\d+)\s*дн', duration_str)
    if day_match:
        days = int(day_match.group(1))
        return max(1, days // 30)

    # Hours - convert (assume 160 hours = 1 month)
    hour_match = re.search(r'(\d+[,.]?\d*)\s*час', duration_str)
    if hour_match:
        hours = float(hour_match.group(1).replace(',', '.'))
        return max(1, int(hours / 160))

    # Minutes - very short courses
    min_match = re.search(r'(\d+)\s*минут', duration_str)
    if min_match:
        return 1

    # Lessons - assume 4 lessons per month
    lesson_match = re.search(r'(\d+)\s*занят', duration_str)
    if lesson_match:
        lessons = int(lesson_match.group(1))
        return max(1, lessons // 4)

    return 1


def map_level(level: str) -> str:
    """Map parser level to site level."""
    if not level:
        return "Начинающий"
    level_lower = level.lower()
    if level_lower in ("beginner", "начальный", "базовый", "с нуля", "junior"):
        return "Начинающий"
    elif level_lower in ("intermediate", "средний", "middle"):
        return "Средний"
    elif level_lower in ("advanced", "продвинутый", "professional", "профессионал", "senior", "expert", "pro"):
        return "Продвинутый"
    return "Начинающий"


def get_school_logo(school: str) -> str:
    """Get short logo for school."""
    logos = {
        "Skillbox": "SB",
        "GeekBrains": "GB",
        "Яндекс Практикум": "ЯП",
        "Нетология": "НТ",
        "Coursera": "CR",
        "OTUS": "OT",
        "AgileFluent": "AF",
        "QA Studio": "QA",
        "Институт психологии Smart": "IP",
        "Skypro": "SP",
        "Skyeng": "SE",
        "SF Education": "SF",
        "REBOTICA": "RB",
        "Skysmart": "SM",
        "Эльбрус буткемп": "ЭБ",
        "Skillfactory": "SF",
        "Бруноям": "БЯ",
        "Contented": "CN",
        "Pikabu Courses": "PC",
    }
    return logos.get(school, school[:2].upper())


def get_category_from_title(title: str, school: str) -> str:
    """Infer category from title and school."""
    title_lower = title.lower()

    # Programming keywords
    prog_keywords = ['python', 'разработчик', 'developer', 'programming', 'java', 'javascript',
                     'react', 'node', 'django', 'flask', 'spring', 'go ', 'golang', 'c++', 'c#',
                     'unity', 'unreal', 'game', 'игр', 'ios', 'swift', 'android', 'kotlin',
                     'fullstack', 'backend', 'frontend', 'web', 'веб', 'ml', 'machine learning',
                     'data science', 'data analyst', 'sql', 'database', 'devops', 'docker',
                     'kubernetes', 'linux', 'администратор', 'системный', 'qa', 'тестировани',
                     'testing', 'автотест', 'c++', 'rust', 'php', 'laravel', 'symfony']

    # Design keywords
    design_keywords = ['дизайн', 'design', 'ui', 'ux', 'figma', 'photoshop', 'illustrator',
                       'брендинг', 'branding', 'типографика', 'графический', '3d', 'blender',
                       'after effects', 'motion', 'анимация']

    # Marketing keywords
    marketing_keywords = ['маркетолог', 'marketing', 'smm', 'seo', 'контекстная', 'реклама',
                          'таргет', 'email', 'контент', 'performance', 'crM', 'автоматизац']

    # Analytics keywords
    analytics_keywords = ['аналитик', 'analyst', 'data', 'tableau', 'power bi', 'excel',
                          'статистик', 'визуализац', 'bi ', 'business intelligence']

    # Management keywords
    mgmt_keywords = ['менеджер', 'manager', 'продукт', 'product', 'project', 'проект',
                     'agile', 'scrum', 'roadmap', 'руководит', 'лидер']

    # Finance keywords
    finance_keywords = ['финанс', 'finance', 'бухгалтер', 'инвестиц', 'оценка', 'моделирован',
                        'валют', 'банк', 'credit', 'риск']

    if any(kw in title_lower for kw in prog_keywords):
        return "Программирование"
    elif any(kw in title_lower for kw in design_keywords):
        return "Дизайн"
    elif any(kw in title_lower for kw in marketing_keywords):
        return "Маркетинг"
    elif any(kw in title_lower for kw in analytics_keywords):
        return "Аналитика"
    elif any(kw in title_lower for kw in mgmt_keywords):
        return "Менеджмент"
    elif any(kw in title_lower for kw in finance_keywords):
        return "Финансы"

    # Default by school
    school_defaults = {
        "Skillbox": "Программирование",
        "GeekBrains": "Программирование",
        "AgileFluent": "Маркетинг",
        "QA Studio": "Программирование",
        "Институт психологии Smart": "Менеджмент",
    }
    return school_defaults.get(school, "Программирование")


def get_image_for_category(category: str) -> str:
    """Get a placeholder image URL based on category."""
    images = {
        "Программирование": "https://images.pexels.com/photos/574077/pexels-photo-574077.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Дизайн": "https://images.pexels.com/photos/5649518/pexels-photo-5649518.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Маркетинг": "https://images.pexels.com/photos/5912284/pexels-photo-5912284.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Аналитика": "https://images.pexels.com/photos/5912280/pexels-photo-5912280.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Менеджмент": "https://images.pexels.com/photos/6326370/pexels-photo-6326370.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
        "Финансы": "https://images.pexels.com/photos/4497757/pexels-photo-4497757.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600",
    }
    return images.get(category, images["Программирование"])


def extract_tags(title: str, description: str = "") -> list:
    """Extract relevant tags from title and description."""
    text = (title + " " + description).lower()
    tag_map = {
        "Python": ["python", "питон"],
        "JavaScript": ["javascript", "js ", "typescript", "ts "],
        "React": ["react", "reactjs"],
        "Node.js": ["node.js", "nodejs", "node "],
        "Django": ["django"],
        "SQL": ["sql", "postgresql", "mysql", "база данных"],
        "HTML/CSS": ["html", "css", "верстка", "frontend"],
        "Java": ["java ", "spring"],
        "Go": ["golang", "go "],
        "C++": ["c++", "cpp"],
        "C#": ["c#", ".net", "dotnet"],
        "Unity": ["unity"],
        "Unreal Engine": ["unreal", "ue5"],
        "Swift": ["swift", "ios"],
        "Kotlin": ["kotlin", "android"],
        "Figma": ["figma"],
        "Photoshop": ["photoshop", "фотошоп"],
        "Illustrator": ["illustrator", "иллюстратор"],
        "UX/UI": ["ux", "ui", "пользователь"],
        "Machine Learning": ["machine learning", "ml ", "нейронн", "tensorflow", "pytorch"],
        "Data Science": ["data science", "дата саенс"],
        "DevOps": ["devops", "docker", "kubernetes", "ci/cd"],
        "Testing": ["тестирован", "qa ", "автотест", "selenium", "playwright"],
        "SEO": ["seo", "сEO"],
        "SMM": ["smm", "социальн"],
        "Google Ads": ["google ads", "яндекс директ", "контекстная"],
        "Excel": ["excel", "эксель"],
        "Tableau": ["tableau"],
        "Power BI": ["power bi", "powerbi"],
        "Agile": ["agile", "scrum", "аджайл"],
        "Project Management": ["project management", "управление проект"],
        "Product Management": ["product management", "продукт"],
    }

    tags = []
    for tag, keywords in tag_map.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)

    # Add category-specific defaults if no tags found
    if not tags:
        default_tags = {
            "Программирование": ["Programming", "Code"],
            "Дизайн": ["Design", "Creative"],
            "Маркетинг": ["Marketing", "Digital"],
            "Аналитика": ["Analytics", "Data"],
            "Менеджмент": ["Management", "Leadership"],
            "Финансы": ["Finance", "Analytics"],
        }
        # We don't have category here, so just add generic
        tags = ["Course"]

    return tags[:6]  # Limit to 6 tags


def convert_course(parsed: dict, course_id: int) -> dict:
    """Convert a parsed course to the site's TypeScript format."""
    source = parsed.get("source", "unknown")
    # Determine school from source if not explicitly provided
    school = parsed.get("school")
    if not school:
        school_map = {
            "skillbox": "Skillbox",
            "geekbrains": "GeekBrains",
            "pikabu": parsed.get("school", "Pikabu Courses"),
        }
        school = school_map.get(source, source.capitalize())

    title = parsed.get("title", "Untitled Course")
    url = parsed.get("course_url") or parsed.get("url", "#")
    price_str = parsed.get("price", "Цена не указана")
    duration_str = parsed.get("duration", "")
    level = parsed.get("level", "beginner")
    description = parsed.get("description", "")
    rating = parsed.get("rating", 4.5)
    review_count = parsed.get("review_count", 0)
    click_count = parsed.get("click_count", 0)

    price_num = parse_price_to_number(price_str)
    duration_months = parse_duration_to_months(duration_str)
    level_mapped = map_level(level)
    category = get_category_from_title(title, school)
    school_logo = get_school_logo(school)
    image = get_image_for_category(category)
    tags = extract_tags(title, description)

    # Estimate students count from click_count or review_count
    students_count = max(click_count, review_count * 50, 100)

    # Determine if hot/new based on rating and review count
    is_hot = rating >= 4.8 and review_count > 20
    is_new = click_count > 5000

    # Old price - estimate 20-30% higher for non-free courses
    old_price = None
    if price_num > 0:
        old_price = int(price_num * 1.25)

    return {
        "id": course_id,
        "title": title,
        "school": school,
        "schoolLogo": school_logo,
        "category": category,
        "description": description[:300] + ("..." if len(description) > 300 else ""),
        "price": price_num,
        "oldPrice": old_price,
        "duration": duration_months,
        "level": level_mapped,
        "rating": round(rating, 1) if rating else 4.5,
        "reviewsCount": review_count,
        "studentsCount": students_count,
        "image": image,
        "tags": tags,
        "isHot": is_hot,
        "isNew": is_new,
        "certificate": True,
        "url": url,  # Add the actual course URL
    }


def main():
    print("Fetching courses from all sources...")

    all_courses = []
    course_id = 1

    # Fetch Skillbox
    print("\n1. Fetching Skillbox courses...")
    try:
        skillbox_courses = parse_skillbox_courses()
        print(f"   Found {len(skillbox_courses)} courses")
        for c in skillbox_courses:
            all_courses.append(convert_course(c, course_id))
            course_id += 1
    except Exception as e:
        print(f"   Error: {e}")

    # Fetch GeekBrains
    print("\n2. Fetching GeekBrains courses...")
    try:
        geekbrains_courses = parse_geekbrains_courses()
        print(f"   Found {len(geekbrains_courses)} courses")
        for c in geekbrains_courses:
            all_courses.append(convert_course(c, course_id))
            course_id += 1
    except Exception as e:
        print(f"   Error: {e}")

    # Fetch Pikabu
    print("\n3. Fetching Pikabu courses...")
    try:
        pikabu_courses = parse_pikabu_courses()
        print(f"   Found {len(pikabu_courses)} courses")
        for c in pikabu_courses:
            all_courses.append(convert_course(c, course_id))
            course_id += 1
    except Exception as e:
        print(f"   Error: {e}")

    print(f"\nTotal courses: {len(all_courses)}")

    # Generate TypeScript file
    ts_content = generate_typescript(all_courses)

    output_path = "/home/nikon/test/edu/site-agregator/site/src/data/courses.ts"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ts_content)

    print(f"\nWritten to {output_path}")

    # Print stats
    schools = {}
    categories = {}
    for c in all_courses:
        schools[c["school"]] = schools.get(c["school"], 0) + 1
        categories[c["category"]] = categories.get(c["category"], 0) + 1

    print("\nBy school:")
    for school, count in sorted(schools.items(), key=lambda x: -x[1]):
        print(f"  {school}: {count}")

    print("\nBy category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")


def generate_typescript(courses: list) -> str:
    """Generate TypeScript file content."""

    # Type definition
    lines = [
        "export type Course = {",
        "  id: number;",
        "  title: string;",
        "  school: string;",
        "  schoolLogo: string;",
        "  category: string;",
        "  description: string;",
        "  price: number;",
        "  oldPrice?: number;",
        "  duration: number; // months",
        "  level: \"Начинающий\" | \"Средний\" | \"Продвинутый\";",
        "  rating: number;",
        "  reviewsCount: number;",
        "  studentsCount: number;",
        "  image: string;",
        "  tags: string[];",
        "  isHot?: boolean;",
        "  isNew?: boolean;",
        "  certificate: boolean;",
        "  url: string;  // Link to the actual course page",
        "};",
        "",
        "export const schools = [",
    ]

    # Unique schools
    unique_schools = sorted(set(c["school"] for c in courses))
    for school in unique_schools:
        lines.append(f"  \"{school}\",")
    lines.append("];")
    lines.append("")

    # Categories
    lines.append("export const categories = [")
    unique_categories = sorted(set(c["category"] for c in courses))
    lines.append("  \"Все\",")
    for cat in unique_categories:
        lines.append(f"  \"{cat}\",")
    lines.append("];")
    lines.append("")

    # Courses array
    lines.append("export const courses: Course[] = [")

    for c in courses:
        lines.append("  {")
        lines.append(f"    id: {c['id']},")
        title_escaped = c['title'].replace('"', '\\"')
        school_escaped = c['school'].replace('"', '\\"')
        desc_escaped = c['description'].replace('"', '\\"')
        lines.append(f"    title: \"{title_escaped}\",")
        lines.append(f"    school: \"{school_escaped}\",")
        lines.append(f"    schoolLogo: \"{c['schoolLogo']}\",")
        lines.append(f"    category: \"{c['category']}\",")
        lines.append(f"    description: \"{desc_escaped}\",")
        lines.append(f"    price: {c['price']},")
        if c['oldPrice']:
            lines.append(f"    oldPrice: {c['oldPrice']},")
        lines.append(f"    duration: {c['duration']},")
        lines.append(f"    level: \"{c['level']}\",")
        lines.append(f"    rating: {c['rating']},")
        lines.append(f"    reviewsCount: {c['reviewsCount']},")
        lines.append(f"    studentsCount: {c['studentsCount']},")
        lines.append(f"    image: \"{c['image']}\",")
        lines.append(f"    tags: {json.dumps(c['tags'], ensure_ascii=False)},")
        if c['isHot']:
            lines.append(f"    isHot: true,")
        if c['isNew']:
            lines.append(f"    isNew: true,")
        lines.append(f"    certificate: {str(c['certificate']).lower()},")
        lines.append(f"    url: \"{c['url']}\",")
        lines.append("  },")

    lines.append("];")

    return "\n".join(lines)


if __name__ == "__main__":
    main()