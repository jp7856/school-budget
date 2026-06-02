import requests
import json
import os
import sys
from datetime import datetime, timedelta
from urllib.parse import urlencode

API_KEY = os.environ["NARAJANGTER_API_KEY"]

def get_date_range():
    if len(sys.argv) == 3:
        from_date = sys.argv[1] + "0000"
        to_date   = sys.argv[2] + "2359"
    elif len(sys.argv) == 2:
        from_date = sys.argv[1] + "0000"
        to_date   = sys.argv[1] + "2359"
    else:
        now = datetime.now()
        from_date = (now - timedelta(days=30)).strftime("%Y%m%d") + "0000"
        to_date   = now.strftime("%Y%m%d") + "2359"
    print(f"📅 조회 기간: {from_date} ~ {to_date}")
    return from_date, to_date

def fetch_all(from_date, to_date):
    base_url = "http://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoThng"
    all_items = []
    page = 1

    while True:
        query = urlencode({
            "pageNo": str(page),
            "numOfRows": "100",
            "inqryDiv": "1",
            "inqryBgnDt": from_date,
            "inqryEndDt": to_date,
            "type": "json",
        })
        url = f"{base_url}?serviceKey={API_KEY}&{query}"

        try:
            res = requests.get(url, timeout=15)
            print(f"  페이지 {page}: 상태코드 {res.status_code}")
            data = res.json()
            items = data.get("response", {}).get("body", {}).get("items", [])
            if isinstance(items, dict):
                items = [items]
            if not items:
                break
            all_items.extend(items)
            total = int(data.get("response", {}).get("body", {}).get("totalCount", 0))
            print(f"  → {len(all_items)}/{total}건 수집")
            if len(all_items) >= total:
                break
            page += 1
        except Exception as e:
            print(f"❌ 오류: {e}")
            break

    return all_items

if __name__ == "__main__":
    from_date, to_date = get_date_range()
    print("🔍 나라장터 입찰공고 수집 중...")
    items = fetch_all(from_date, to_date)
    print(f"✅ 총 {len(items)}건 수집 완료")

    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "from": from_date,
        "to": to_date,
        "total": len(items),
        "items": items
    }

    with open("bids.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("💾 bids.json 저장 완료")
