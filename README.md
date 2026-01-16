# NVIDIA 일일 주가 추적기 (NVIDIA Daily Stock Tracker)

NVIDIA(NVDA)의 일일 주가 변동과 관련 뉴스를 자동으로 추적하여 Excel 파일에 기록하는 도구입니다.

## 주요 기능

- **일일 주가 데이터 수집**: 시가, 종가, 최고가, 최저가, 거래량
- **변동률 계산**: 전일 대비 변동 금액 및 변동률 자동 계산
- **뉴스 수집**: 해당 날짜의 NVIDIA 관련 뉴스 자동 수집
- **Excel 자동 저장**: 데이터를 Excel 파일에 자동으로 누적 저장
- **중복 방지**: 같은 날짜의 데이터는 업데이트됨

## 설치 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

필요한 패키지:
- pandas: 데이터 처리
- openpyxl: Excel 파일 작성
- requests: 웹 API 호출

### 2. 프로젝트 구조

```
test-repo/
├── finance_util.py           # 핵심 유틸리티 함수들
├── nvda_daily_tracker.py     # 메인 실행 스크립트
├── requirements.txt          # 의존성 패키지 목록
├── nvda_daily_tracker.xlsx   # 생성되는 추적 데이터 (자동 생성)
└── README.md                 # 이 파일
```

## 사용 방법

### 기본 사용 (오늘 날짜)

```bash
python nvda_daily_tracker.py
```

### 특정 날짜 지정

```bash
python nvda_daily_tracker.py 2026-01-15
```

### 출력 디렉토리 지정

```bash
python nvda_daily_tracker.py 2026-01-15 /path/to/output
```

## Excel 파일 구조

생성되는 `nvda_daily_tracker.xlsx` 파일은 다음과 같은 열로 구성됩니다:

| 열 이름 | 설명 |
|---------|------|
| 날짜 | 거래 날짜 (YYYY-MM-DD) |
| 전일종가 | 전 거래일 종가 |
| 시가 | 당일 시가 |
| 종가 | 당일 종가 |
| 최고가 | 당일 최고가 |
| 최저가 | 당일 최저가 |
| 거래량 | 거래량 |
| 변동가격 | 전일 대비 변동 금액 |
| 변동률(%) | 전일 대비 변동률 |
| 뉴스/이유 | 당일 관련 뉴스 요약 |

## 출력 예시

```
============================================================
NVIDIA 일일 주가 추적기
============================================================

오늘 날짜로 추적합니다: 2026-01-15

📊 NVIDIA(NVDA) 주가 데이터를 가져오는 중...

날짜: 2026-01-15
전일 종가: $145.23
시가: $146.00
종가: $148.75
최고가: $149.50
최저가: $145.80
거래량: 45,678,900
변동: $3.52 (2.42%)

📰 뉴스를 가져오는 중...

총 3개의 뉴스를 찾았습니다:
1. [Reuters] NVIDIA announces new AI chip breakthrough
   발행: 2026-01-15 09:30:00
   링크: https://...

💾 Excel 파일에 기록을 저장하는 중...

✅ 성공적으로 기록되었습니다!
파일 위치: nvda_daily_tracker.xlsx

============================================================
추적 완료!
============================================================
```

## 함수 설명

### finance_util.py

#### `fetch_daily_stock_data(symbol, date=None)`
- Yahoo Finance API를 사용하여 주가 데이터 가져오기
- symbol: 주식 티커 (예: 'NVDA')
- date: 조회할 날짜 (None이면 오늘)

#### `fetch_stock_news(symbol, date=None, max_results=5)`
- Google News RSS를 사용하여 뉴스 가져오기
- symbol: 주식 티커
- date: 조회할 날짜
- max_results: 최대 뉴스 개수

#### `append_daily_record(stock_data, news_summary, filename, output_dir=None)`
- Excel 파일에 일일 기록 추가
- 파일이 없으면 새로 생성
- 같은 날짜가 이미 있으면 업데이트

## 활용 방법

### 1. 매일 자동 실행 (크론잡)

```bash
# 매일 오후 5시에 실행
0 17 * * * cd /path/to/repo && python nvda_daily_tracker.py
```

### 2. 과거 데이터 수집

```bash
# 최근 일주일 데이터 수집 (예시)
for date in 2026-01-09 2026-01-10 2026-01-13 2026-01-14 2026-01-15; do
    python nvda_daily_tracker.py $date
    sleep 2
done
```

### 3. 프로그래밍 방식 사용

```python
from finance_util import fetch_daily_stock_data, fetch_stock_news, append_daily_record

# 주가 데이터 가져오기
stock_data = fetch_daily_stock_data('NVDA', '2026-01-15')
print(f"종가: ${stock_data['close']}, 변동률: {stock_data['change_pct']}%")

# 뉴스 가져오기
news = fetch_stock_news('NVDA', '2026-01-15')
for item in news:
    print(f"{item['title']} - {item['publisher']}")

# Excel에 저장
news_summary = " | ".join([f"{n['title']}" for n in news[:3]])
append_daily_record(stock_data, news_summary)
```

## 장기 분석 활용

이 도구로 수집한 데이터를 사용하여:

1. **주가 변동 패턴 분석**: 날짜별 변동률과 뉴스의 상관관계 파악
2. **뉴스 영향도 분석**: 특정 뉴스 키워드와 주가 변동의 관계 분석
3. **장기 트렌드 파악**: 누적된 데이터로 장기 추세 분석
4. **이벤트 영향 측정**: 특정 이벤트(실적 발표, 신제품 출시 등)의 영향도 측정

## 데이터 소스

- **주가 데이터**: Yahoo Finance API
- **뉴스 데이터**: Google News RSS Feed

## 주의사항

1. **거래일 한정**: 주말과 공휴일은 가장 최근 거래일의 데이터가 반환됩니다
2. **네트워크 필수**: 인터넷 연결이 필요합니다
3. **API 제한**: 과도한 요청은 차단될 수 있으니 적절한 간격을 두고 실행하세요
4. **뉴스 정확도**: 뉴스는 자동 수집되므로 관련성을 직접 확인해야 합니다

## 문제 해결

### 주가 데이터를 가져올 수 없을 때
- 인터넷 연결 확인
- Yahoo Finance API 접근 가능 여부 확인
- 프록시 설정 확인

### 뉴스를 가져올 수 없을 때
- Google News RSS 접근 가능 여부 확인
- 뉴스가 없을 경우 "뉴스 없음"으로 기록됨

### Excel 파일 오류
- 파일이 다른 프로그램에서 열려있지 않은지 확인
- 출력 디렉토리에 쓰기 권한이 있는지 확인

## 라이선스

MIT License

## 기여

개선 사항이나 버그 리포트는 이슈로 등록해주세요.
