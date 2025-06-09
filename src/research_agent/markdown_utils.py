from __future__ import annotations

import re
import html


def to_html(markdown_text: str) -> str:
    """Convert a subset of markdown to HTML (headers, bold, italic, code)."""
    text = html.escape(markdown_text)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'(.+?)', r'<code>\1</code>', text)
    paragraphs = re.split(r'\n{2,}', text)
    parts = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<h'):
            parts.append(f'<p>{p}</p>')
        elif p:
            parts.append(p)
    return '\n'.join(parts)


def strip_markdown(text: str) -> str:
    """Remove common markdown formatting, returning plain text."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', text)
    text = re.sub(r'(.+?)', r'\1', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    return text.strip()
