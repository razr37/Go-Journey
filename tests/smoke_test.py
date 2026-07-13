from pathlib import Path
import re
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
html = HTML.read_text(encoding="utf-8")

# 1) JavaScript syntax check
scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
assert scripts, "No inline JavaScript found"
js_path = ROOT / "tests" / "_inline_app.js"
js_path.write_text(scripts[0], encoding="utf-8")
subprocess.run(["node", "--check", str(js_path)], check=True)
js_path.unlink(missing_ok=True)

# 2) Browser smoke test on a mobile viewport
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path="/usr/bin/chromium",
        args=["--no-sandbox"],
    )
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.set_content(html, wait_until="load")
    page.wait_for_timeout(150)

    card_text = page.locator("#lessonCard").inner_text().strip()
    assert len(card_text) > 40, "Lesson card is blank"
    assert "recovered" not in card_text.lower(), card_text

    for button_id in ("resetBtn", "hintBtn", "demoBtn"):
        assert page.locator(f"#{button_id}").is_enabled(), f"{button_id} disabled"

    page.locator("#hintBtn").click()
    page.wait_for_timeout(30)
    assert len(page.locator("#feedback").inner_text().strip()) > 5

    # Switch directly into Reading Mode and verify card/controls.
    page.evaluate("current=puzzles.find(p=>p.chapter==='Puzzle Book'); buildBoard(); renderCard();")
    page.wait_for_timeout(50)
    reading_text = page.locator("#lessonCard").inner_text()
    assert "to play" in reading_text
    assert "Reading mode" in reading_text

    page.locator("#whyBtn").click()
    assert page.locator("#whyBox").evaluate("e => e.classList.contains('show')")
    page.locator("#whyBox .why-close").click()
    assert not page.locator("#whyBox").evaluate("e => e.classList.contains('show')")

    # Correct move must unlock Continue.
    page.evaluate("const a=current.answers[0]; getPoint(a[0],a[1]).click();")
    page.wait_for_timeout(50)
    assert page.locator("#continueBtn").is_enabled(), "Correct move did not unlock Continue"

    assert not errors, f"Browser runtime errors: {errors}"
    browser.close()

print("GO_JOURNEY_SMOKE_TEST_PASS")
