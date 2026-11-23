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
            assert parsed.netloc in {"github.com", "arxiv.org"}
            assert (parsed.netloc == "github.com" and (parsed.path == "/reddydev-ai" or parsed.path.startswith("/reddydev-ai/"))) or (parsed.netloc == "arxiv.org" and parsed.path == "/abs/2601.03273"), f"Unexpected external link: {href}"
    assert "INTERVIEW_WALKTHROUGH" not in text, "Interview-preparation content is not homepage navigation"
    assert "Seven-minute interview walkthrough" not in text
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


def test_published_status_and_release_decisions_cannot_regress_to_starter_copy():
    site = SITE.read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    decision = (ROOT / "docs" / "RELEASE_DECISION_RECORD.md").read_text(encoding="utf-8")
    guide = (ROOT / "docs" / "PUBLISHING_GUIDE.md").read_text(encoding="utf-8")

    assert "Design accountable AI." in site
    assert 'class="evidence-table"' in site
    assert 'id="approach"' in site
    assert "GuardEval" in site and "academic moderation benchmark" in site
    assert "The public backend was" in (ROOT / "PORTFOLIO.md").read_text(encoding="utf-8")
    assert "https://reddydev-ai.github.io/guardeval/" in readme
    assert "GitHub Pages has **not** been enabled or published" not in readme
    assert "profile repository once that repository exists" not in readme
    assert "not affiliated" in readme.lower() and "arxiv.org/abs/2601.03273" in readme
    assert "https://github.com/reddydev-ai/reddydev-ai/blob/main/README.md" in guide
    for value in ["5 scripted cases", "6 scripted cases", "NOT MEASURED", "NOT IMPLEMENTED"]:
        assert value in decision
    assert "0.70" in decision and "illustrative defaults" in decision
