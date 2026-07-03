from __future__ import annotations

import re


def normalize_url(url: str) -> str:
    """Strip trailing slashes and lowercase scheme+host."""
    url = url.strip()
    url = re.sub(r"/+$", "", url)
    parts = url.split("://", 1)
    if len(parts) == 2:
        scheme, rest = parts
        host, *path = rest.split("/", 1)
        return f"{scheme.lower()}://{host.lower()}" + ("/" + path[0] if path else "")
    return url.lower()


def extract_domain(url: str) -> str:
    """Extract domain (host) from a URL string."""
    url = normalize_url(url)
    match = re.search(r"://([^/]+)", url)
    return match.group(1) if match else url


def is_likely_paywalled(url: str) -> bool:
    """Heuristic: flag URLs from known paywalled domains."""
    paywalled = {"wsj.com", "ft.com", "nytimes.com", "bloomberg.com", "economist.com"}
    domain = extract_domain(url)
    return any(domain.endswith(p) for p in paywalled)
