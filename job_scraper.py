import html
import requests
from bs4 import BeautifulSoup


def fetch_demo_jobs(company_slug="discord", keyword="engineer", limit=10):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    raw_jobs = response.json().get("jobs", [])
    clean_jobs = []

    for job in raw_jobs:
        title = job.get("title", "")

        # Filter by keyword so you only score relevant roles
        if keyword.lower() not in title.lower():
            continue

        # Greenhouse double-escapes HTML entities in its JSON feed
        unescaped_html = html.unescape(job.get("content", ""))
        clean_text = BeautifulSoup(unescaped_html, "html.parser").get_text(
            separator="\n", strip=True
        )

        clean_jobs.append({
            "title": title,
            "location": job.get("location", {}).get("name", "Unknown"),
            "url": job.get("absolute_url", ""),
            "description": clean_text,
        })

        if len(clean_jobs) >= limit:
            break

    return clean_jobs


if __name__ == "__main__":
    # Example: Fetch 3 engineering jobs from Discord's live career board
    jobs = fetch_demo_jobs(company_slug="discord", keyword="engineer", limit=3)

    for j in jobs:
        print(f"Title: {j['title']} ({j['location']})")
        print(f"Preview: {j['description']}\n")
