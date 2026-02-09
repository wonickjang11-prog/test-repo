"""
StockAnalysis.com 재무제표 데이터 스크래퍼

stockanalysis.com에서 주식 재무제표(Income Statement) 테이블을 다운로드하여
CSV 및 Excel 파일로 저장합니다.

사용법:
    python scrape_stock_financials.py                    # NVDA 분기별 (기본값)
    python scrape_stock_financials.py --ticker AAPL      # AAPL 분기별
    python scrape_stock_financials.py --period annual    # NVDA 연간
    python scrape_stock_financials.py --output my_data   # 출력 파일명 지정

필수 패키지:
    pip install selenium beautifulsoup4 pandas openpyxl

Chrome/Chromium 브라우저 및 ChromeDriver가 설치되어 있어야 합니다.
    - ChromeDriver: https://chromedriver.chromium.org/downloads
    - 또는: pip install webdriver-manager
"""

import argparse
import sys
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def create_driver():
    """헤드리스 Chrome WebDriver를 생성합니다."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )

    try:
        # webdriver-manager가 설치되어 있으면 자동으로 ChromeDriver를 관리
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except ImportError:
        # webdriver-manager가 없으면 시스템 PATH에서 chromedriver를 찾음
        driver = webdriver.Chrome(options=options)

    return driver


def build_url(ticker, period="quarterly", statement="financials"):
    """StockAnalysis URL을 생성합니다.

    Args:
        ticker: 주식 티커 (예: 'NVDA')
        period: 'quarterly' 또는 'annual'
        statement: 'financials' (Income Statement),
                   'balance-sheet', 'cash-flow-statement'
    """
    base = f"https://stockanalysis.com/stocks/{ticker.lower()}/{statement}/"
    if period == "quarterly":
        base += "?p=quarterly"
    return base


def scrape_financials(ticker="NVDA", period="quarterly", statement="financials"):
    """StockAnalysis.com에서 재무제표 테이블을 스크래핑합니다.

    Args:
        ticker: 주식 티커 심볼
        period: 'quarterly' 또는 'annual'
        statement: 재무제표 종류

    Returns:
        pandas.DataFrame: 재무제표 데이터
    """
    url = build_url(ticker, period, statement)
    print(f"URL: {url}")
    print(f"데이터를 가져오는 중...")

    driver = create_driver()

    try:
        driver.get(url)

        # 테이블이 로드될 때까지 대기 (최대 20초)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        # JS 렌더링 완료를 위한 추가 대기
        time.sleep(2)

        # 페이지 소스를 BeautifulSoup으로 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")

        if not table:
            raise RuntimeError("페이지에서 테이블을 찾을 수 없습니다.")

        # 헤더 추출
        headers = []
        thead = table.find("thead")
        if thead:
            for th in thead.find_all("th"):
                headers.append(th.get_text(strip=True))

        # 데이터 행 추출
        rows = []
        tbody = table.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cells:
                    rows.append(cells)

        if not rows:
            raise RuntimeError("테이블에 데이터가 없습니다.")

        # DataFrame 생성
        # 첫 번째 헤더는 행 라벨(metric name), 나머지는 기간(분기/연도)
        df = pd.DataFrame(rows, columns=headers if headers else None)

        # 첫 번째 열을 인덱스로 설정 (metric 이름)
        if not df.empty and len(df.columns) > 0:
            df = df.set_index(df.columns[0])

        print(f"성공: {len(df)} 행 x {len(df.columns)} 열 데이터를 가져왔습니다.")
        return df

    finally:
        driver.quit()


def save_data(df, output_name, ticker, period):
    """DataFrame을 CSV와 Excel 파일로 저장합니다."""
    if output_name:
        base_name = output_name
    else:
        base_name = f"{ticker.lower()}_{period}_financials"

    csv_path = f"{base_name}.csv"
    xlsx_path = f"{base_name}.xlsx"

    df.to_csv(csv_path, encoding="utf-8-sig")
    print(f"CSV 저장: {csv_path}")

    df.to_excel(xlsx_path, engine="openpyxl")
    print(f"Excel 저장: {xlsx_path}")

    return csv_path, xlsx_path


def main():
    parser = argparse.ArgumentParser(
        description="StockAnalysis.com 재무제표 데이터 다운로더"
    )
    parser.add_argument(
        "--ticker", default="NVDA", help="주식 티커 심볼 (기본값: NVDA)"
    )
    parser.add_argument(
        "--period",
        choices=["quarterly", "annual"],
        default="quarterly",
        help="기간 (기본값: quarterly)",
    )
    parser.add_argument(
        "--statement",
        choices=["financials", "balance-sheet", "cash-flow-statement"],
        default="financials",
        help="재무제표 종류 (기본값: financials = Income Statement)",
    )
    parser.add_argument("--output", default=None, help="출력 파일명 (확장자 제외)")
    parser.add_argument(
        "--print", dest="print_table", action="store_true", help="결과를 터미널에 출력"
    )

    args = parser.parse_args()

    try:
        df = scrape_financials(args.ticker, args.period, args.statement)

        if args.print_table:
            print("\n" + "=" * 80)
            print(df.to_string())
            print("=" * 80)

        csv_path, xlsx_path = save_data(df, args.output, args.ticker, args.period)
        print(f"\n완료! 파일이 저장되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
