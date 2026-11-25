import html
import re
import requests
from bs4 import BeautifulSoup


def fetch_demo_jobs(company_slug="discord", keyword="engineer", limit=10):
    company_slug = company_slug.strip().strip("/")
    if not company_slug:
        raise ValueError("Enter a Greenhouse board slug.")
    if limit < 1:
        raise ValueError("The job limit must be at least 1.")

    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    raw_jobs = response.json().get("jobs", [])
    clean_jobs = []

    for job in raw_jobs:
        title = job.get("title", "")

        # Filter by keyword so you only score relevant roles
        if keyword and keyword.lower() not in title.lower():
            continue

        # Greenhouse double-escapes HTML entities in its JSON feed
        unescaped_html = html.unescape(job.get("content", ""))
        clean_text = BeautifulSoup(unescaped_html, "html.parser").get_text(
            separator="\n", strip=True
        )

        description = clean_text
        clean_jobs.append({
            "title": title,
            "location": job.get("location", {}).get("name", "Unknown"),
            "url": job.get("absolute_url", ""),
            "description": description,
        })

        if len(clean_jobs) >= limit:
            break

    return clean_jobs


def required_experience_years(description):
    """Estimate explicitly stated minimum years of experience, if present."""
    patterns = (
        r"(?:at least|minimum of|min\.?|a minimum of)\s+(\d+)\+?\s+years?",
        r"(\d+)\+?\s+years?\s+(?:of\s+)?(?:relevant\s+)?experience\s+(?:required|minimum)",
    )
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0


if __name__ == "__main__":
    # Example: Fetch 3 engineering jobs from Discord's live career board
    jobs = fetch_demo_jobs(company_slug="discord", keyword="engineer", limit=3)

    for j in jobs:
        print(f"Title: {j['title']} ({j['location']})")
        print(f"Preview: {j['description']}\n")
