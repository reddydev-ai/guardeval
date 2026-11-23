// Browser-rendered audit of the deployed, zero-cost portfolio.
// Uses real Chromium on GitHub Actions; captures desktop/mobile screenshots.
// Distinguishes rendered layout verification from a manual design review.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

const liveUrl = 'https://reddydev-ai.github.io/guardeval/';
const localUrl = pathToFileURL(path.resolve(__dirname, '../docs/index.html')).href;
const outDir = path.resolve(__dirname, '../visual-qa-artifacts');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({
    channel: 'chrome',
    headless: true,
    args: ['--no-sandbox'],
  });
  const reports = [];
  try {
    for (const [label, width, height] of [
      ['desktop', 1440, 900],
      ['mobile', 390, 844],
    ]) {
      const page = await browser.newPage({
        viewport: { width, height },
        deviceScaleFactor: 1,
      });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const response = await page.goto(liveUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
      assert.equal(response.status(), 200, 'Published portfolio URL must return HTTP 200');
      await page.locator('h1').waitFor({ state: 'visible' });
      await page.locator('.project').first().waitFor({ state: 'visible' });
      const audit = await page.evaluate(() => {
        const projectCards = [...document.querySelectorAll('article.project')];
        const heading = document.querySelector('h1');
        const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
        const nav = document.querySelector('nav');
        const grid = document.querySelector('.grid');
        const read = el => {
          const r = el.getBoundingClientRect();
          return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width),
                   height: Math.round(r.height), right: Math.round(r.right) };
        };
        return {
          title: document.title,
          language: document.documentElement.lang,
          documentWidth: document.documentElement.scrollWidth,
          viewportWidth: window.innerWidth,
          headingText: heading.textContent.trim(),
          heading: read(heading),
          nav: read(nav),
          cards: projectCards.map(c => ({ title: c.querySelector('h3')?.textContent,
                                         box: read(c) })),
          projectsGridColumns: getComputedStyle(grid).gridTemplateColumns,
          localAnchorsValid: links.filter(h => h && h.startsWith('#'))
            .every(h => document.getElementById(h.slice(1)) !== null),
          trustedOutbound: links.filter(h => h && /^https?:/.test(h))
            .every(h => { const u = new URL(h); return u.hostname === "github.com" || (u.hostname === "arxiv.org" && u.pathname === "/abs/2601.03273"); }),
          hasMissingImage: [...document.images].some(img => !img.complete || img.naturalWidth === 0),
          visibleSections: ['projects','verification','approach','limits']
            .every(id => document.getElementById(id) !== null),
          renderedTextLength: document.body.innerText.trim().length,
        };
      });
      assert.equal(audit.language, 'en');
      assert.match(audit.headingText, /Design accountable AI.*Show the evidence/s);
      assert.equal(audit.cards.length, 3);
      assert.deepEqual(audit.cards.map(c => c.title), ['PolicyMind','FlowAgent','GuardEval']);
      assert.equal(audit.localAnchorsValid, true);
      assert.equal(audit.trustedOutbound, true);
      assert.equal(audit.visibleSections, true);
      assert.equal(audit.hasMissingImage, false);
      assert.ok(audit.renderedTextLength > 1000, 'Content is unexpectedly empty');
      assert.ok(audit.documentWidth <= width + 1, 'Horizontal overflow: ' + JSON.stringify(audit));
      assert.ok(audit.heading.width > width * .35, 'Hero heading width suspicious');
      assert.equal(errors.length, 0, 'Page JS errors: ' + errors.join('; '));
      if (label === 'mobile') {
        assert.ok(audit.cards.every(c => c.box.width > width * .80), 'Mobile cards should stack');
        assert.ok(audit.cards[1].box.y > audit.cards[0].box.y, 'Mobile cards overlap vertically');
      } else {
        assert.ok(audit.cards[1].box.x > audit.cards[0].box.x, 'Desktop cards should be side by side');
      }
      await page.screenshot({ path: path.join(outDir, label + '.png'), fullPage: true });
      const local = await browser.newPage({ viewport: { width, height } });
      await local.goto(localUrl, { waitUntil: 'load' });
      const sourceNames = await local.locator('article.project h3').allTextContents();
      assert.deepEqual(sourceNames.map(s => s.trim()), audit.cards.map(c => c.title),
                       'Published card titles differ from checked-in source');
      reports.push({ viewport: label, url: liveUrl, http: 200, verdict: 'pass',
                     screenshot: label + '.png', ...audit });
      await local.close();
      await page.close();
    }
    fs.writeFileSync(path.join(outDir, 'browser-audit.json'), JSON.stringify(reports, null, 2) + '\n');
    for (const report of reports) console.log('RENDERED_PORTFOLIO_AUDIT ' + JSON.stringify(report));
  } finally {
    await browser.close();
  }
})().catch(err => {
  console.error('RENDERED_PORTFOLIO_AUDIT_FAILED', err);
  process.exitCode = 1;
});
