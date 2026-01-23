#!/usr/bin/env python3
"""
Gemini Gem 리서치 내용 추출 도구
사용법: python gemini_export.py <gem_url>
"""

import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print("❌ Selenium이 설치되지 않았습니다.")
    print("설치 명령: pip install selenium")
    sys.exit(1)


def setup_driver():
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 이미 로그인된 브라우저 프로필 사용 (선택사항)
    # chrome_options.add_argument('--user-data-dir=/home/user/.config/google-chrome')

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_content(driver, url):
    """Gemini Gem 페이지에서 콘텐츠 추출"""
    print(f"📡 페이지 로딩 중: {url}")
    driver.get(url)

    # 페이지 로드 대기
    print("⏳ 로그인 및 콘텐츠 로딩을 기다립니다...")
    print("   브라우저가 열리면 수동으로 로그인하세요.")
    time.sleep(10)  # 로그인 시간 대기

    # 페이지가 완전히 로드될 때까지 대기
    try:
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    except Exception as e:
        print(f"⚠️  페이지 로딩 타임아웃: {e}")

    # 동적 콘텐츠 로딩 대기
    print("⏳ 동적 콘텐츠 로딩 중...")
    time.sleep(5)

    # JavaScript로 콘텐츠 추출
    content = driver.execute_script("""
        const content = [];

        // 제목 추출
        const title = document.querySelector('h1, [role="heading"]');
        if (title) {
            content.push('='.repeat(80));
            content.push('제목: ' + title.innerText.trim());
            content.push('='.repeat(80));
            content.push('');
        }

        // 모든 메시지 콘텐츠
        const messages = document.querySelectorAll(
            '[data-test-id*="message"], .message, [class*="message"], article, [role="article"]'
        );
        messages.forEach((msg, idx) => {
            const text = msg.innerText.trim();
            if (text && text.length > 10) {
                content.push('\\n--- 섹션 ' + (idx + 1) + ' ---');
                content.push(text);
                content.push('');
            }
        });

        // 전체 페이지 텍스트 백업
        if (content.length < 5) {
            const body = document.body.innerText;
            content.push('\\n--- 전체 페이지 내용 ---');
            content.push(body);
        }

        return content.join('\\n');
    """)

    return content


def save_content(content, output_file=None):
    """콘텐츠를 파일로 저장"""
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'gemini_research_{timestamp}.txt'

    output_path = Path(output_file)
    output_path.write_text(content, encoding='utf-8')
    print(f"✅ 저장 완료: {output_path.absolute()}")
    print(f"📊 추출된 콘텐츠 크기: {len(content):,} 문자")

    # 미리보기
    preview = content[:500]
    print(f"\n--- 미리보기 (처음 500자) ---")
    print(preview)
    if len(content) > 500:
        print("...")


def main():
    if len(sys.argv) < 2:
        print("사용법: python gemini_export.py <gem_url> [output_file]")
        print("예시: python gemini_export.py https://gemini.google.com/gem/2978c017455c/f84d19cbb2532ab8")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    driver = None
    try:
        driver = setup_driver()
        content = extract_content(driver, url)

        if content and len(content.strip()) > 100:
            save_content(content, output_file)
        else:
            print("⚠️  콘텐츠를 추출할 수 없습니다. 로그인이 필요하거나 페이지 구조가 다를 수 있습니다.")
            print("💡 브라우저 콘솔 스크립트(gemini_export_browser.js)를 사용해보세요.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("\n⏳ 5초 후 브라우저를 닫습니다...")
            time.sleep(5)
            driver.quit()


if __name__ == '__main__':
    main()
