# Gemini Gem 리서치 내용 추출 가이드

Gemini Gem에 저장된 딥 리서치 내용을 텍스트로 다운로드하는 방법 모음입니다.

## 📋 목차

1. [방법 1: 브라우저 콘솔 스크립트 (가장 간단)](#방법-1-브라우저-콘솔-스크립트)
2. [방법 2: Python + Selenium](#방법-2-python--selenium)
3. [방법 3: Python + Playwright (권장)](#방법-3-python--playwright)
4. [방법 4: 수동 복사](#방법-4-수동-복사)

---

## 방법 1: 브라우저 콘솔 스크립트

**가장 빠르고 간단한 방법입니다!**

### 단계:

1. Gemini Gem 페이지를 브라우저에서 엽니다
   ```
   https://gemini.google.com/gem/2978c017455c/f84d19cbb2532ab8
   ```

2. **F12** 키를 눌러 개발자 도구를 엽니다

3. **Console** 탭으로 이동합니다

4. `gemini_export_browser.js` 파일의 내용을 복사하여 콘솔에 붙여넣고 **Enter**를 누릅니다

5. 자동으로 `.txt` 파일이 다운로드됩니다!

### 장점:
- ✅ 설치 불필요
- ✅ 가장 빠름
- ✅ 로그인 상태 그대로 사용

### 단점:
- ❌ 수동 실행 필요
- ❌ 여러 Gem을 반복 처리하기 어려움

---

## 방법 2: Python + Selenium

### 설치:

```bash
pip install selenium
```

Chrome 드라이버 설치 (자동):
```bash
pip install webdriver-manager
```

### 사용법:

```bash
python gemini_export.py https://gemini.google.com/gem/2978c017455c/f84d19cbb2532ab8
```

출력 파일명 지정:
```bash
python gemini_export.py <gem_url> my_research.txt
```

### 장점:
- ✅ 자동화 가능
- ✅ 여러 URL 처리 용이

### 단점:
- ❌ 드라이버 설정 필요
- ❌ 안정성이 다소 떨어질 수 있음

---

## 방법 3: Python + Playwright (권장)

**가장 안정적이고 강력한 방법입니다!**

### 설치:

```bash
pip install playwright
playwright install chromium
```

### 사용법:

```bash
python gemini_export_playwright.py https://gemini.google.com/gem/2978c017455c/f84d19cbb2532ab8
```

출력 파일명 지정:
```bash
python gemini_export_playwright.py <gem_url> my_research.txt
```

### 실행 과정:

1. 브라우저가 자동으로 열립니다
2. 로그인이 필요하면 수동으로 로그인하세요 (30초 대기)
3. 자동으로 콘텐츠를 추출하여 저장합니다
4. 스크린샷도 함께 저장됩니다

### 장점:
- ✅ 가장 안정적
- ✅ 스크린샷 자동 저장
- ✅ 최신 웹 기술 지원
- ✅ 여러 URL 배치 처리 가능

### 단점:
- ❌ 초기 설치가 다소 복잡

---

## 방법 4: 수동 복사

프로그래밍 도구 없이 수동으로 복사하는 방법:

### 단계:

1. Gemini Gem 페이지를 엽니다
2. **Ctrl+A** (모두 선택)
3. **Ctrl+C** (복사)
4. 텍스트 에디터에 붙여넣기
5. `.txt` 파일로 저장

### 장점:
- ✅ 가장 단순
- ✅ 설치 불필요

### 단점:
- ❌ 시간 소모적
- ❌ 서식이 깨질 수 있음
- ❌ 반복 작업에 비효율적

---

## 🎯 추천 방법

| 상황 | 추천 방법 |
|------|----------|
| 한 번만 추출 필요 | 방법 1 (브라우저 콘솔) |
| 여러 Gem 반복 추출 | 방법 3 (Playwright) |
| Python 환경 없음 | 방법 1 또는 방법 4 |
| 최고 안정성 필요 | 방법 3 (Playwright) |

---

## 🔧 고급 사용법

### 여러 URL 배치 처리 (Playwright)

```python
import subprocess

urls = [
    "https://gemini.google.com/gem/xxx/yyy",
    "https://gemini.google.com/gem/aaa/bbb",
    # 더 많은 URL...
]

for i, url in enumerate(urls):
    output = f"research_{i+1}.txt"
    subprocess.run(["python", "gemini_export_playwright.py", url, output])
```

### 쿠키 저장하여 로그인 자동화

Playwright 스크립트에서 로그인 후 쿠키를 저장:

```python
# 로그인 후
context.storage_state(path="auth_state.json")

# 다음 실행 시
context = browser.new_context(storage_state="auth_state.json")
```

---

## 🐛 문제 해결

### "403 Forbidden" 오류
- **원인**: 로그인 필요
- **해결**: 브라우저 콘솔 방법(방법 1) 또는 Playwright로 수동 로그인

### 콘텐츠가 비어있음
- **원인**: 페이지 로딩 시간 부족
- **해결**: Python 스크립트의 `time.sleep()` 시간 증가

### Playwright 설치 오류
```bash
# 권한 문제 시
sudo playwright install chromium

# 의존성 설치
sudo playwright install-deps
```

---

## 📝 파일 설명

| 파일 | 설명 |
|------|------|
| `gemini_export_browser.js` | 브라우저 콘솔용 JavaScript |
| `gemini_export.py` | Selenium 버전 |
| `gemini_export_playwright.py` | Playwright 버전 (권장) |

---

## 💡 팁

1. **스크린샷 함께 저장**: Playwright는 자동으로 스크린샷을 저장합니다
2. **정기 백업**: cron/스케줄러로 정기적 백업 가능
3. **포맷 유지**: Markdown 포맷이 필요하면 HTML 추출 후 변환
4. **대용량 처리**: 매우 긴 리서치는 섹션별로 나눠 처리

---

## 📞 지원

문제가 발생하면:
1. 브라우저 콘솔의 오류 메시지 확인
2. Python 스크립트의 오류 로그 확인
3. Gemini 페이지 구조가 변경되었을 수 있음 (스크립트 업데이트 필요)

---

## ⚖️ 법적 고지

- 개인 용도로만 사용하세요
- Gemini 서비스 약관을 준수하세요
- 추출한 콘텐츠의 저작권을 존중하세요
