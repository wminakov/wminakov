#!/usr/bin/env python3
"""Refresh the three most recently updated public repositories in README.md."""
import json
import os
import re
from urllib.request import Request, urlopen

USERNAME = "wminakov"
README = "README.md"
START = "<!-- LATEST-REPOS:START -->"
END = "<!-- LATEST-REPOS:END -->"
EXCLUDED = {"wminakov"}
LIMIT = 3


def fetch_repositories():
    url = f"https://api.github.com/users/{USERNAME}/repos?type=owner&sort=updated&direction=desc&per_page=100"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-profile-readme-updater",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def render(repos):
    eligible = [
        repo for repo in repos
        if not repo.get("fork")
        and not repo.get("archived")
        and not repo.get("private")
        and repo.get("name") not in EXCLUDED
    ]
    eligible.sort(key=lambda item: item.get("pushed_at") or item.get("updated_at") or "", reverse=True)
    selected = eligible[:LIMIT]
    if not selected:
        return "_No additional public projects yet._"

    lines = []
    for repo in selected:
        line = f"- [**{repo['name']}**]({repo['html_url']})"
        description = (repo.get("description") or "").replace("\n", " ").strip()
        if description:
            line += f" — {description}"
        lines.append(line)
    return "\n".join(lines)


def main():
    with open(README, "r", encoding="utf-8") as file:
        content = file.read()
    if START not in content or END not in content:
        raise SystemExit("README markers were not found.")
    repos = fetch_repositories()
    replacement = START + "\n" + render(repos) + "\n" + END
    updated = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: replacement, content, flags=re.S)
    if updated != content:
        with open(README, "w", encoding="utf-8") as file:
            file.write(updated)


if __name__ == "__main__":
    main()
