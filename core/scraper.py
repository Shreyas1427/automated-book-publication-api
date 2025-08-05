import uuid
from pathlib import Path
from playwright.sync_api import sync_playwright
import logging
from multiprocessing import Queue



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_chapter_sync(url: str) -> dict:
   
    Path("screenshots").mkdir(exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            content_element = page.locator(".mw-parser-output")
            content_element.wait_for(timeout=10000)
            text = content_element.inner_text()

            if not text or len(text.split()) < 100:
                raise ValueError("Scraped content is missing or too short.")

            screenshot_filename = f"chapter_raw_{uuid.uuid4()}.png"
            screenshot_path = Path("screenshots") / screenshot_filename
            page.screenshot(path=screenshot_path, full_page=True)
            browser.close()

            return {
                "status": "success",
                "text": text,
                "screenshot_path": str(screenshot_path),
                "source_url": url,
            }
    except Exception as e:
        return {"status": "failure", "error": str(e)}

def scrape_worker(url: str, queue: Queue):
    logging.info(f"Separate process started for scraping {url}")
    result = scrape_chapter_sync(url)
    queue.put(result)
    logging.info("Separate process finished scraping and put result in queue.")