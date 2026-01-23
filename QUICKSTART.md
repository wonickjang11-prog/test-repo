# 빠른 시작 가이드 (5분 안에!)

Gemini Gem 리서치를 텍스트로 다운로드하는 가장 빠른 방법입니다.

---

## 🚀 가장 빠른 방법 (프로그래밍 지식 불필요!)

### 단계 1: Gemini Gem 페이지 열기
브라우저에서 이 URL을 엽니다:
```
https://gemini.google.com/gem/2978c017455c/f84d19cbb2532ab8
```

### 단계 2: 개발자 도구 열기
키보드에서 **F12** 키를 누릅니다
(Mac: `Cmd + Option + I`)

### 단계 3: Console 탭 클릭
상단 탭에서 **Console**을 클릭합니다

### 단계 4: 코드 복사 & 붙여넣기

1. `gemini_export_browser.js` 파일을 엽니다
2. 전체 내용을 복사합니다 (`Ctrl+A`, `Ctrl+C`)
3. Console에 붙여넣습니다 (`Ctrl+V`)

**참고**: "allow pasting"을 입력하라는 메시지가 나오면 그대로 입력하세요

### 단계 5: 실행
**Enter** 키를 누릅니다

### 단계 6: 완료!
`.txt` 파일이 자동으로 다운로드됩니다! 🎉

**소요 시간**: 약 30초

---

## 🐍 Python을 사용하는 방법 (프로그래머용)

### 설치 (최초 1회만)

```bash
pip install playwright
playwright install chromium
```

### 실행

```bash
python gemini_export_playwright.py https://gemini.google.com/gem/2978c017455c/f84d19cbb2532ab8
```

브라우저가 열리면 로그인하고 30초 기다리면 자동으로 저장됩니다!

---

## 📚 더 자세한 가이드

- **브라우저 방법 상세**: `BROWSER_CONSOLE_GUIDE.md` 참고
- **Python 방법 상세**: `GEMINI_EXPORT_README.md` 참고
- **문제 해결**: 위 문서들의 "문제 해결" 섹션 참고

---

## ❓ 자주 묻는 질문

**Q: F12를 눌러도 아무 일도 안 일어나요**
A: 브라우저 설정에서 개발자 도구가 비활성화되었을 수 있습니다. 마우스 오른쪽 클릭 → "검사" 시도해보세요.

**Q: 코드를 붙여넣을 수 없어요**
A: Console에 `allow pasting`을 입력하고 Enter를 누른 후 다시 시도하세요.

**Q: 파일이 비어있어요**
A: 페이지가 완전히 로드된 후에 다시 시도하세요. 로그인이 필요할 수도 있습니다.

**Q: Python 없이 할 수 있나요?**
A: 네! 위의 "가장 빠른 방법"은 Python 없이 브라우저만으로 가능합니다.

---

## 🎯 방법 선택 가이드

| 상황 | 추천 방법 | 파일 |
|------|----------|------|
| 프로그래밍 모름 | 브라우저 콘솔 | `gemini_export_browser.js` |
| 한 번만 추출 | 브라우저 콘솔 | `gemini_export_browser.js` |
| 여러 번 반복 | Python Playwright | `gemini_export_playwright.py` |
| 자동화 필요 | Python Playwright | `gemini_export_playwright.py` |

---

**시작하세요!** 위의 "가장 빠른 방법"을 따라하면 5분 안에 완료됩니다. 👍
