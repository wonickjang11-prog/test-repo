#!/usr/bin/env python3
"""
NVIDIA Daily Stock Tracker - Demo Version

이 데모 버전은 샘플 데이터를 사용하여 네트워크 연결 없이 추적기의 작동 방식을 보여줍니다.
"""

import sys
from datetime import datetime
import pandas as pd
import os


def get_sample_stock_data():
    """샘플 주가 데이터 반환 (2026년 1월 16일 기준)"""
    return {
        'date': '2026-01-16',
        'prev_close': 142.50,
        'open': 143.20,
        'close': 145.80,
        'high': 146.50,
        'low': 142.80,
        'volume': 45230000,
        'change': 3.30,
        'change_pct': 2.32
    }


def get_sample_news():
    """샘플 뉴스 데이터 반환"""
    return [
        {
            'title': 'NVIDIA Announces New AI Chip Architecture',
            'publisher': 'Reuters',
            'link': 'https://example.com/news1',
            'published': '2026-01-16 09:30:00'
        },
        {
            'title': 'China Market Access Boosts NVIDIA Stock',
            'publisher': 'Bloomberg',
            'link': 'https://example.com/news2',
            'published': '2026-01-16 10:15:00'
        },
        {
            'title': 'Data Center Demand Drives NVIDIA Growth',
            'publisher': 'CNBC',
            'link': 'https://example.com/news3',
            'published': '2026-01-16 11:00:00'
        }
    ]


def format_news_summary(news_items):
    """뉴스 항목들을 요약 문자열로 변환"""
    if not news_items:
        return "뉴스 없음"

    summary_parts = []
    for i, news in enumerate(news_items[:3], 1):
        title = news['title']
        publisher = news['publisher']
        summary_parts.append(f"{i}. [{publisher}] {title}")

    return " | ".join(summary_parts)


def save_to_excel(stock_data, news_summary, filename='nvda_demo_tracker.xlsx'):
    """데이터를 Excel 파일에 저장"""
    # 새 레코드 생성
    new_record = pd.DataFrame([{
        '날짜': stock_data['date'],
        '전일종가': stock_data['prev_close'],
        '시가': stock_data['open'],
        '종가': stock_data['close'],
        '최고가': stock_data['high'],
        '최저가': stock_data['low'],
        '거래량': stock_data['volume'],
        '변동가격': stock_data['change'],
        '변동률(%)': stock_data['change_pct'],
        '뉴스/이유': news_summary
    }])

    # 파일이 존재하면 기존 데이터와 병합
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename, engine='openpyxl')

        # 같은 날짜가 있으면 업데이트, 없으면 추가
        if stock_data['date'] in existing_df['날짜'].values:
            existing_df.loc[existing_df['날짜'] == stock_data['date']] = new_record.iloc[0]
            df = existing_df
        else:
            df = pd.concat([existing_df, new_record], ignore_index=True)
    else:
        df = new_record

    # 날짜순 정렬 (최신순)
    df['날짜'] = pd.to_datetime(df['날짜'])
    df = df.sort_values('날짜', ascending=False)
    df['날짜'] = df['날짜'].dt.strftime('%Y-%m-%d')

    # Excel 파일 저장
    df.to_excel(filename, index=False, engine='openpyxl')
    return filename


def track_nvda_demo():
    """NVIDIA 주가 추적 데모 실행"""
    print("=" * 60)
    print("NVIDIA 일일 주가 추적기 (데모 버전)")
    print("=" * 60)
    print("\n📊 샘플 데이터를 사용하여 추적 기능을 시연합니다.\n")

    try:
        # 1. 샘플 주가 데이터 가져오기
        print("📊 NVIDIA(NVDA) 주가 데이터를 가져오는 중...")
        stock_data = get_sample_stock_data()

        print(f"\n날짜: {stock_data['date']}")
        print(f"전일 종가: ${stock_data['prev_close']}")
        print(f"시가: ${stock_data['open']}")
        print(f"종가: ${stock_data['close']}")
        print(f"최고가: ${stock_data['high']}")
        print(f"최저가: ${stock_data['low']}")
        print(f"거래량: {stock_data['volume']:,}")
        print(f"변동: ${stock_data['change']} ({stock_data['change_pct']:+.2f}%)")

        # 변동 방향 표시
        if stock_data['change'] > 0:
            print("📈 상승")
        elif stock_data['change'] < 0:
            print("📉 하락")
        else:
            print("➡️  보합")

        # 2. 샘플 뉴스 가져오기
        print(f"\n📰 뉴스를 가져오는 중...")
        news_items = get_sample_news()

        print(f"\n총 {len(news_items)}개의 뉴스를 찾았습니다:")
        for i, news in enumerate(news_items, 1):
            print(f"{i}. [{news['publisher']}] {news['title']}")
            print(f"   발행: {news['published']}")
            print(f"   링크: {news['link']}")

        # 3. 뉴스 요약
        news_summary = format_news_summary(news_items)

        # 4. Excel에 저장
        print(f"\n💾 Excel 파일에 기록을 저장하는 중...")
        filepath = save_to_excel(stock_data, news_summary)

        print(f"\n✅ 성공적으로 기록되었습니다!")
        print(f"파일 위치: {os.path.abspath(filepath)}")

        # 5. 저장된 데이터 미리보기
        print(f"\n📋 저장된 데이터 미리보기:")
        df = pd.read_excel(filepath, engine='openpyxl')
        print(df.to_string(index=False))

        print("\n" + "=" * 60)
        print("추적 완료!")
        print("=" * 60)
        print("\n💡 실제 버전은 Yahoo Finance API에서 실시간 데이터를 가져옵니다.")
        print("💡 nvda_daily_tracker.py 스크립트를 사용하세요.")

        return 0

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(track_nvda_demo())
