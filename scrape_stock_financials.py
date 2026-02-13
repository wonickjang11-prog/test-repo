"""
StockAnalysis.com 재무제표 데이터 스크래퍼

stockanalysis.com에서 주식 재무제표(Income Statement) 테이블을 다운로드하여
CSV 및 Excel 파일로 저장합니다.

사용법:
    python scrape_stock_financials.py                    # NVDA 분기별 (기본값)
    python scrape_stock_financials.py --ticker AAPL      # AAPL 분기별
    python scrape_stock_financials.py --period annual    # NVDA 연간
    python scrape_stock_financials.py --output my_data   # 출력 파일명 지정
    python scrape_stock_financials.py --visible          # Chrome 창 보이게 실행

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


def create_driver(headless=True):
    """Chrome WebDriver를 생성합니다."""
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")

    try:
        # Selenium 4.6+ 은 자체 Selenium Manager로 ChromeDriver를 자동 관리
        driver = webdriver.Chrome(options=options)
    except Exception as e1:
        try:
            # 실패 시 webdriver-manager로 재시도
            from webdriver_manager.chrome import ChromeDriverManager

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e2:
            print(f"\nChrome WebDriver 초기화 실패:")
            print(f"  시도 1 (Selenium Manager): {e1}")
            print(f"  시도 2 (webdriver-manager): {e2}")
            print("\n해결 방법:")
            print("  1. Chrome 브라우저가 설치되어 있는지 확인하세요")
            print("  2. 패키지를 업그레이드하세요:")
            print("     python -m pip install --upgrade selenium")
            sys.exit(1)

    return driver


def build_url(ticker, period="quarterly", statement="financials"):
    """StockAnalysis URL을 생성합니다."""
    base = f"https://stockanalysis.com/stocks/{ticker.lower()}/{statement}/"
    if period == "quarterly":
        base += "?p=quarterly"
    return base


def scrape_financials(ticker="NVDA", period="quarterly", statement="financials",
                      headless=True):
    """StockAnalysis.com에서 재무제표 테이블을 스크래핑합니다."""
    url = build_url(ticker, period, statement)
    print(f"URL: {url}")
    print(f"데이터를 가져오는 중... (headless={headless})")

    driver = create_driver(headless=headless)

    try:
        driver.get(url)
        print(f"페이지 로딩 중... (최대 30초 대기)")

        # 테이블이 로드될 때까지 대기
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")

        if not table:
            raise RuntimeError("페이지에서 테이블을 찾을 수 없습니다.")

        # 헤더 추출 - thead의 마지막 tr만 사용 (상위 행은 그룹 헤더일 수 있음)
        headers = []
        thead = table.find("thead")
        if thead:
            header_rows = thead.find_all("tr")
            if header_rows:
                last_header_row = header_rows[-1]
                for th in last_header_row.find_all("th"):
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

        # 헤더와 데이터 열 수가 맞지 않으면 데이터 기준으로 조정
        num_cols = len(rows[0])
        if headers and len(headers) != num_cols:
            print(f"  헤더({len(headers)}개)와 데이터({num_cols}개) 열 수 불일치, 조정 중...")
            if len(headers) > num_cols:
                headers = headers[:num_cols]
            else:
                headers = headers + [f"Col_{i}" for i in range(len(headers), num_cols)]

        df = pd.DataFrame(rows, columns=headers if headers else None)

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
    parser.add_argument(
        "--visible", action="store_true",
        help="Chrome 창을 보이게 실행 (headless 모드 끔)"
    )

    args = parser.parse_args()
    headless = not args.visible

    try:
        df = scrape_financials(args.ticker, args.period, args.statement,
                               headless=headless)

        if args.print_table:
            print("\n" + "=" * 80)
            print(df.to_string())
            print("=" * 80)

        csv_path, xlsx_path = save_data(df, args.output, args.ticker, args.period)
        print(f"\n완료! 파일이 저장되었습니다.")

    except Exception as e:
        error_msg = str(e)
        print(f"\n오류 발생: {error_msg}", file=sys.stderr)
        if "Could not reach host" in error_msg or "ERR_" in error_msg:
            print("\n네트워크 문제 해결 방법:", file=sys.stderr)
            print("  1. --visible 옵션으로 다시 시도하세요:", file=sys.stderr)
            print(f"     python scrape_stock_financials.py --visible", file=sys.stderr)
            print("  2. 방화벽/백신이 Chrome을 차단하는지 확인하세요", file=sys.stderr)
            print("  3. VPN을 사용 중이라면 끄고 다시 시도하세요", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
