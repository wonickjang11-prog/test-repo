#!/usr/bin/env python3
"""
NVIDIA Daily Stock Tracker

이 스크립트는 NVIDIA(NVDA)의 일일 주가 변동과 이유를 추적합니다.
매일 실행하여 주가 데이터와 뉴스를 수집하고 Excel 파일에 저장합니다.
"""

import sys
from datetime import datetime
from finance_util import fetch_daily_stock_data, fetch_stock_news, append_daily_record


def format_news_summary(news_items):
    """
    뉴스 항목들을 요약 문자열로 변환합니다.

    Args:
        news_items (list): 뉴스 항목 리스트

    Returns:
        str: 뉴스 요약 문자열
    """
    if not news_items:
        return "뉴스 없음"

    summary_parts = []
    for i, news in enumerate(news_items[:3], 1):  # 최대 3개 뉴스
        title = news['title']
        publisher = news['publisher']
        summary_parts.append(f"{i}. [{publisher}] {title}")

    return " | ".join(summary_parts)


def track_nvda_daily(date=None, output_dir=None):
    """
    NVIDIA의 일일 주가를 추적하고 기록합니다.

    Args:
        date (str): 추적할 날짜 (YYYY-MM-DD 형식, None이면 오늘)
        output_dir (str): 출력 디렉토리 경로 (None이면 현재 디렉토리)

    Returns:
        dict: 추적 결과 정보
    """
    symbol = 'NVDA'

    try:
        # 1. 주가 데이터 가져오기
        print(f"📊 NVIDIA(NVDA) 주가 데이터를 가져오는 중...")
        stock_data = fetch_daily_stock_data(symbol, date)

        print(f"\n날짜: {stock_data['date']}")
        print(f"전일 종가: ${stock_data['prev_close']}")
        print(f"시가: ${stock_data['open']}")
        print(f"종가: ${stock_data['close']}")
        print(f"최고가: ${stock_data['high']}")
        print(f"최저가: ${stock_data['low']}")
        print(f"거래량: {stock_data['volume']:,}")
        print(f"변동: ${stock_data['change']} ({stock_data['change_pct']}%)")

        # 2. 뉴스 가져오기
        print(f"\n📰 뉴스를 가져오는 중...")
        news_items = fetch_stock_news(symbol, stock_data['date'])

        if news_items:
            print(f"\n총 {len(news_items)}개의 뉴스를 찾았습니다:")
            for i, news in enumerate(news_items, 1):
                print(f"{i}. [{news['publisher']}] {news['title']}")
                print(f"   발행: {news['published']}")
                print(f"   링크: {news['link']}")
        else:
            print("관련 뉴스를 찾지 못했습니다.")

        # 3. 뉴스 요약
        news_summary = format_news_summary(news_items)

        # 4. Excel에 기록 추가
        print(f"\n💾 Excel 파일에 기록을 저장하는 중...")
        filepath = append_daily_record(stock_data, news_summary, output_dir=output_dir)

        print(f"\n✅ 성공적으로 기록되었습니다!")
        print(f"파일 위치: {filepath}")

        return {
            'success': True,
            'date': stock_data['date'],
            'close': stock_data['close'],
            'change_pct': stock_data['change_pct'],
            'news_count': len(news_items),
            'filepath': filepath
        }

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}", file=sys.stderr)
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("NVIDIA 일일 주가 추적기")
    print("=" * 60)

    # 명령행 인자 처리
    date = None
    output_dir = None

    if len(sys.argv) > 1:
        date = sys.argv[1]
        print(f"\n지정된 날짜: {date}")
    else:
        print(f"\n오늘 날짜로 추적합니다: {datetime.now().strftime('%Y-%m-%d')}")

    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
        print(f"출력 디렉토리: {output_dir}")

    print()

    # 추적 실행
    result = track_nvda_daily(date, output_dir)

    if result['success']:
        print("\n" + "=" * 60)
        print("추적 완료!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("추적 실패")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
