#!/usr/bin/env python3
"""
Gemini Gem 리서치 내용 추출 도구 (Playwright 버전)
사용법: python gemini_export_playwright.py <gem_url>
"""

import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Playwright가 설치되지 않았습니다.")
    print("설치 명령:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)


def extract_content_with_playwright(url, headless=False):
    """Playwright를 사용하여 Gemini Gem 페이지에서 콘텐츠 추출"""
    print(f"📡 Playwright 시작...")

    with sync_playwright() as p:
        # 브라우저 실행 (headless=False면 UI 표시)
        browser = p.chromium.launch(headless=headless)

        # 컨텍스트 생성 (로그인 정보 유지 가능)
        context = browser.new_context()

        # 쿠키 로드 (있다면)
        # context.add_cookies(cookies)  # 미리 저장한 쿠키 사용 가능

        page = context.new_page()

        print(f"📡 페이지 로딩: {url}")
        page.goto(url, wait_until='networkidle', timeout=60000)

        if not headless:
            print("⏳ 로그인이 필요하면 브라우저에서 로그인하세요.")
            print("   로그인 후 30초 대기합니다...")
            time.sleep(30)

        # 콘텐츠 로딩 대기
        print("⏳ 콘텐츠 로딩 중...")
        time.sleep(5)

        # JavaScript로 콘텐츠 추출
        content = page.evaluate("""
            () => {
                const content = [];

                // URL과 타임스탬프
                content.push('URL: ' + window.location.href);
                content.push('추출 시간: ' + new Date().toLocaleString('ko-KR'));
                content.push('='.repeat(80));
                content.push('');

                // 제목 추출
                const titleSelectors = [
                    'h1',
                    '[role="heading"]',
                    '[class*="title"]',
                    '.title'
                ];

                for (const selector of titleSelectors) {
                    const title = document.querySelector(selector);
                    if (title && title.innerText.trim()) {
                        content.push('📌 제목: ' + title.innerText.trim());
                        content.push('='.repeat(80));
                        content.push('');
                        break;
                    }
                }

                // 모든 대화/메시지 콘텐츠 추출
                const messageSelectors = [
                    '[data-test-id*="message"]',
                    '[class*="message"]',
                    'article',
                    '[role="article"]',
                    '[class*="conversation"]',
                    '[class*="chat"]'
                ];

                const foundMessages = new Set();
                messageSelectors.forEach(selector => {
                    const messages = document.querySelectorAll(selector);
                    messages.forEach((msg) => {
                        const text = msg.innerText.trim();
                        // 중복 제거 및 최소 길이 필터
                        if (text && text.length > 20 && !foundMessages.has(text)) {
                            foundMessages.add(text);
                        }
                    });
                });

                // 메시지 정렬 및 추가
                if (foundMessages.size > 0) {
                    Array.from(foundMessages).forEach((text, idx) => {
                        content.push('\\n' + '─'.repeat(80));
                        content.push('📝 섹션 ' + (idx + 1));
                        content.push('─'.repeat(80));
                        content.push(text);
                        content.push('');
                    });
                }

                // 특정 리서치 콘텐츠 추출
                const researchContainers = document.querySelectorAll(
                    '[class*="research"], [class*="deep-dive"], [data-type*="research"]'
                );
                researchContainers.forEach((container, idx) => {
                    const text = container.innerText.trim();
                    if (text && text.length > 50) {
                        content.push('\\n' + '═'.repeat(80));
                        content.push('🔬 리서치 ' + (idx + 1));
                        content.push('═'.repeat(80));
                        content.push(text);
                        content.push('');
                    }
                });

                // 백업: 전체 본문 텍스트
                if (content.length < 10) {
                    content.push('\\n' + '═'.repeat(80));
                    content.push('📄 전체 페이지 내용 (백업)');
                    content.push('═'.repeat(80));
                    const main = document.querySelector('main, [role="main"], body');
                    if (main) {
                        content.push(main.innerText);
                    }
                }

                return content.join('\\n');
            }
        """)

        # 스크린샷 저장 (선택사항)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f'gemini_screenshot_{timestamp}.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 스크린샷 저장: {screenshot_path}")

        browser.close()

        return content


def save_content(content, output_file=None):
    """콘텐츠를 파일로 저장"""
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'gemini_research_{timestamp}.txt'

    output_path = Path(output_file)
    output_path.write_text(content, encoding='utf-8')

    print(f"\n✅ 저장 완료: {output_path.absolute()}")
    print(f"📊 추출된 콘텐츠 크기: {len(content):,} 문자")
    print(f"📊 줄 수: {content.count(chr(10)):,} 줄")

    # 미리보기
    lines = content.split('\n')
    preview_lines = lines[:20]
    print(f"\n{'='*80}")
    print(f"미리보기 (처음 20줄)")
    print('='*80)
    for line in preview_lines:
        print(line)
    if len(lines) > 20:
        print(f"... (총 {len(lines)}줄 중 20줄만 표시)")


def main():
    if len(sys.argv) < 2:
        print("사용법: python gemini_export_playwright.py <gem_url> [output_file]")
        print("\n예시:")
        print("  python gemini_export_playwright.py https://gemini.google.com/gem/2978c017455c/f84d19cbb2532ab8")
        print("  python gemini_export_playwright.py <gem_url> output.txt")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        # headless=False로 실행하여 로그인 가능하게 함
        content = extract_content_with_playwright(url, headless=False)

        if content and len(content.strip()) > 100:
            save_content(content, output_file)
            print("\n✅ 추출 완료!")
        else:
            print("\n⚠️  콘텐츠를 추출할 수 없습니다.")
            print("💡 다음을 확인하세요:")
            print("   1. Gemini에 로그인되어 있는지")
            print("   2. URL이 올바른지")
            print("   3. 페이지가 완전히 로드되었는지")

    except PlaywrightTimeout:
        print("❌ 페이지 로딩 타임아웃. 네트워크 연결을 확인하세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
