"""Generate profile cards from public GitHub data using the authenticated gh CLI."""

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER = "specode"
COLORS = {"TypeScript": "#3178c6", "JavaScript": "#c7aa19", "Shell": "#57913b", "Lua": "#6464c8", "Python": "#3572a5"}


def api(endpoint):
    result = subprocess.run(
        ["gh", "api", endpoint], check=True, capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"GitHub returned invalid JSON for {endpoint}") from error


def public_repos():
    repos = []
    page = 1
    while True:
        batch = api(f"users/{USER}/repos?type=owner&per_page=100&page={page}")
        repos.extend(repo for repo in batch if not repo["fork"] and not repo["private"])
        if len(batch) < 100:
            return repos
        page += 1


def text(x, y, value, size=14, color="var(--text)", weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(value))}</text>'


def card(width, title, body, description):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="260" viewBox="0 0 {width} 260" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
<style>
svg {{ --bg: #ffffff; --text: #24292f; --muted: #57606a; --border: #d0d7de; --accent: #2563eb; --track: #eaeef2; }}
@media (prefers-color-scheme: dark) {{ svg {{ --bg: #0d1117; --text: #e6edf3; --muted: #9da7b3; --border: #30363d; --accent: #79a8ff; --track: #21262d; }} }}
text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="259" rx="10" fill="var(--bg)" stroke="var(--border)"/>
{text(24, 38, title, 20, 'var(--accent)', 600)}
{body}
</svg>
'''


def main():
    repos = public_repos()
    user = api(f"users/{USER}")
    languages = Counter()
    for repo in repos:
        # Exclude this profile's generator so it doesn't skew the language chart.
        if repo["name"] != USER:
            languages.update(api(f'repos/{USER}/{repo["name"]}/languages'))

    total = sum(languages.values())
    rows = languages.most_common(5)
    body = []
    summary = []
    for index, (language, count) in enumerate(rows):
        y = 72 + index * 32
        percentage = count / total * 100
        summary.append(f"{language}: {percentage:.1f}%")
        body.append(text(24, y, language, 12))
        body.append(text(278, y, f"{percentage:.1f}%", 12, "var(--muted)"))
        body.append(f'<rect x="24" y="{y + 7}" width="308" height="5" rx="2.5" fill="var(--track)"/>')
        body.append(f'<rect x="24" y="{y + 7}" width="{308 * count / total:.2f}" height="5" rx="2.5" fill="{COLORS.get(language, "#7886a0")}"/>')
    if not rows:
        body.append(text(24, 90, "No language data yet."))
    body.append(text(24, 244, "By bytes · public originals · excludes this profile", 10, "var(--muted)"))
    language_svg = card(360, "Most Used Languages", "\n".join(body), "; ".join(summary) or "No language data")

    stats = [
        ("Stars earned", sum(repo["stargazers_count"] for repo in repos)),
        ("Public original repositories", len(repos)),
        ("Followers", user["followers"]),
        ("Forks of original repositories", sum(repo["forks_count"] for repo in repos)),
    ]
    body = []
    for index, (label, value) in enumerate(stats):
        y = 84 + index * 39
        body.append(text(24, y, label, 15))
        body.append(text(382, y, f"{value:,}", 18, weight=600))
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body.append(text(24, 244, f"Public data only · updated {updated} UTC", 11, "var(--muted)"))
    stats_svg = card(470, "Specode's GitHub Stats", "\n".join(body), "; ".join(f"{label}: {value}" for label, value in stats))

    # Fetch everything successfully before replacing the last good cards.
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "languages.svg").write_text(language_svg, encoding="utf-8")
    (assets / "stats.svg").write_text(stats_svg, encoding="utf-8")


if __name__ == "__main__":
    main()
