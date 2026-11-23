"""Guard the public, zero-cost recruiter portfolio against broken internal links."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs" / "index.html"
PORTFOLIO = ROOT / "PORTFOLIO.md"
PROFILE = ROOT / "docs" / "GITHUB_PROFILE_README_READY.md"

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.hrefs = []
        self.tags = []
        self.lang = None
    def handle_starttag(self, tag, attrs):
        properties = dict(attrs)
        self.tags.append(tag)
        if tag == "html": self.lang = properties.get("lang")
        if properties.get("id"): self.ids.add(properties["id"])
        if tag == "a":
            self.hrefs.append(properties.get("href"))
        if tag in ("script", "iframe", "form", "img", "link"):
            raise AssertionError("Static portfolio cannot include executable or external assets")

def test_static_page_structure_and_links():
    text = SITE.read_text(encoding="utf-8")
    doc = Page()
    doc.feed(text)
    assert text.lstrip().lower().startswith("<!doctype html>")
    assert doc.lang == "en"
    assert "main" in doc.tags and "nav" in doc.tags and "h1" in doc.tags
    assert len(doc.hrefs) >= 12
    assert all(isinstance(href, str) and href for href in doc.hrefs)
    for href in doc.hrefs:
        if href.startswith("#"):
            assert href[1:] in doc.ids, f"Missing anchor target: {href}"
        else:
            parsed = urlparse(href)
            assert parsed.scheme == "https"
            assert parsed.netloc == "github.com"
            assert parsed.path.startswith("/reddydev-ai/"), f"Unexpected external domain or account: {href}"
    assert "independent" in text.lower()
    assert "synthetic" in text.lower()
    assert "not" in text.lower() and "production" in text.lower()

def test_readme_portfolio_is_visible_and_truthful():
    summary = PORTFOLIO.read_text(encoding="utf-8")
    assert all(name in summary for name in ["PolicyMind", "FlowAgent", "GuardEval"])
    assert "not independently reviewed" in summary.lower() or "not independently" in summary.lower()
    assert "not company deployments" in summary.lower()
    profile = PROFILE.read_text(encoding="utf-8")
    assert "https://github.com/reddydev-ai/guardeval/blob/main/PORTFOLIO.md" in profile
    assert "example.com" not in profile
    assert "555-" not in profile
