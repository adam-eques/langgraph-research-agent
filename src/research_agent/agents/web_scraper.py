from __future__ import annotations

import logging
from urllib.parse import urlparse

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from research_agent.config import config
from research_agent.state import ResearchState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a web content extraction specialist. Given raw HTML or text content \
from a web page, extract the most relevant information for the research query.

Tasks:
1. Strip navigation, ads, footers, and boilerplate
2. Preserve key facts, statistics, quotes, and structured content
3. Note the source URL and any publication date found
4. Summarize what the page contributes to the query
"""


def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


def _fetch_page(url: str, timeout: int = 10) -> str:
    """Fetch a URL and return its text content."""
    try:
        import urllib.request

        req = urllib.request.Request(url, headers={"User-Agent": "research-agent/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # Very naive HTML stripping
        import re

        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text)
        return text[:8000]  # cap at 8k chars
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return ""


def build_web_scraper_node():
    llm = ChatAnthropic(
        model=config.default_model,
        temperature=0,
        max_tokens=2048,
        api_key=config.anthropic_api_key,
    )

    def web_scraper(state: ResearchState) -> ResearchState:
        query = state["query"]
        messages = list(state["messages"])

        # Extract URLs from the last researcher message
        import re

        urls: list[str] = []
        if messages:
            content = str(messages[-1].content)
            urls = re.findall(r"https?://[^\s\)\]\"]+", content)
            urls = [u for u in urls if _is_valid_url(u)][:3]  # cap at 3

        if not urls:
            logger.debug("No URLs to scrape")
            return {}

        scraped_notes = []
        for url in urls:
            logger.info("Scraping: %s", url)
            raw_text = _fetch_page(url)
            if not raw_text:
                continue
            response: AIMessage = llm.invoke(
                [
                    SystemMessage(content=_SYSTEM_PROMPT),
                    HumanMessage(
                        content=f"Query: {query}\n\nPage content from {url}:\n\n{raw_text}"
                    ),
                ]
            )
            scraped_notes.append(f"[Scraped: {url}]\n{response.content}")

        return {
            "research_notes": state.get("research_notes", []) + scraped_notes,
            "messages": [AIMessage(content=f"Scraped {len(urls)} pages for additional context.")],
        }

    return web_scraper
