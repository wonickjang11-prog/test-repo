#!/usr/bin/env python3
"""간단한 Gemini Gem 추출 도구"""

import time
from playwright.sync_api import sync_playwright

url = "https://gemini.google.com/gem/2978c017455c/f84d19cbb2532ab8"

print("🚀 브라우저 시작...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print(f"📡 페이지 열기: {url}")
    page.goto(url, timeout=60000)

    print("⏳ 로그인하세요! 30초 기다립니다...")
    time.sleep(30)

    print("📝 텍스트 추출 중...")
    text = page.evaluate("document.body.innerText")

    filename = "gemini_export.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"✅ 저장 완료: {filename}")
    print(f"📊 {len(text):,} 문자 추출됨")

    browser.close()
