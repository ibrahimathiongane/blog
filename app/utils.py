import math
import re
import bleach
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from slugify import slugify as _slugify

# ── Slug ──────────────────────────────────────────────────────────────────────

def make_slug(text: str) -> str:
    """Generate a URL-safe slug from text."""
    return _slugify(text, max_length=200)


# ── Read time ─────────────────────────────────────────────────────────────────

WORDS_PER_MINUTE = 200


def estimate_read_time(markdown_text: str) -> int:
    """Estimate read time in minutes from raw Markdown content."""
    # Strip Markdown syntax for a rough word count
    text = re.sub(r"[#*`>\[\]!_~]", "", markdown_text)
    words = len(text.split())
    minutes = math.ceil(words / WORDS_PER_MINUTE)
    return max(1, minutes)


# ── Markdown renderer ─────────────────────────────────────────────────────────

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p", "pre", "code", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "strong", "em", "a", "img", "table", "thead", "tbody",
    "tr", "th", "td", "hr", "br", "div", "span", "del", "sup", "sub",
]
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "*": ["class", "id"],
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "loading", "width", "height"],
    "code": ["class"],
    "pre": ["class"],
    "div": ["class"],
    "span": ["class"],
}


def render_markdown(text: str) -> str:
    """Convert Markdown to sanitized HTML with syntax highlighting and TOC."""
    md = markdown.Markdown(
        extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(css_class="highlight", linenums=False, guess_lang=True),
            TableExtension(),
            TocExtension(permalink=True),
            "nl2br",
            "sane_lists",
            "attr_list",
        ]
    )
    raw_html = md.convert(text)
    safe_html = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    # bleach escapes some code block content — restore pre/code blocks
    return safe_html


# ── RSS helpers ───────────────────────────────────────────────────────────────

def build_rss_item(article, base_url: str) -> dict:
    return {
        "title": article.title,
        "link": f"{base_url}/blog/{article.slug}",
        "description": article.summary,
        "pubDate": article.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
        if article.published_at
        else "",
        "guid": f"{base_url}/blog/{article.slug}",
    }
