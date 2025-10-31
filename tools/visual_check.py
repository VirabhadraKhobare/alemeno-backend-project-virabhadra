"""Simple Playwright-based visual checker.

Usage:
  - Ensure dependencies are installed: `pip install playwright` and `playwright install`
  - Start the Streamlit app (the script below starts it automatically).
  - Run this script: `python tools/visual_check.py`

This script will:
  - start `streamlit run streamlit_app.py` in the background
  - wait for the app to be reachable at http://localhost:8501
  - use Playwright to capture a desktop and a mobile screenshot
  - save screenshots under `screenshots/`
  - terminate the Streamlit process

Note: This script assumes you are on a development machine with network access to install browsers.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "screenshots"
OUT_DIR.mkdir(exist_ok=True)

STREAMLIT_CMD = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501"]


def wait_for_http(url, timeout=30):
    import socket
    from urllib.request import urlopen

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def run():
    print("Starting Streamlit in background...")
    # start streamlit in background
    proc = subprocess.Popen(STREAMLIT_CMD, cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        url = "http://localhost:8501"
        print(f"Waiting for {url} to become available (30s)...")
        ok = wait_for_http(url, timeout=45)
        if not ok:
            print("Streamlit did not become available in time. Check the server output.")
            return 2

        print("Running Playwright to capture screenshots...")
        # Run Playwright script inline via subprocess to avoid polluting user's env in this file
        pw_script = f"""
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
try:
    # desktop
    browser = p.chromium.launch()
    page = browser.new_page(viewport={{'width': 1366, 'height': 768}})
    page.goto('http://localhost:8501', wait_until='networkidle')
    page.screenshot(path=r'{OUT_DIR / 'layout_desktop.png'}', full_page=True)
    browser.close()

    # mobile
    browser = p.chromium.launch()
    iphone = p.devices['iPhone 12']
    page = browser.new_page(**iphone)
    page.goto('http://localhost:8501', wait_until='networkidle')
    page.screenshot(path=r'{OUT_DIR / 'layout_mobile.png'}', full_page=True)
    browser.close()
finally:
    p.stop()
"""

        # write temporary script
        tmp = REPO_ROOT / "tools" / "_pw_tmp.py"
        tmp.write_text(pw_script)

        # run the script
        # Note: Playwright must be installed and playwright browsers must be installed (playwright install)
        r = subprocess.run([sys.executable, str(tmp)], cwd=str(REPO_ROOT))
        if r.returncode != 0:
            print("Playwright script returned non-zero; ensure Playwright and browsers are installed.")
            return r.returncode

        print(f"Screenshots saved to: {OUT_DIR}")
        return 0
    finally:
        print("Stopping Streamlit...")
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == '__main__':
    sys.exit(run())
