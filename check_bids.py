import requests
import smtplib
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from urllib.parse import urlencode

API_KEY       = os.environ["NARAJANGTER_API_KEY"]
GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PW  = os.environ["GMAIL_APP_PASSWORD"]
RECV_EMAIL    = os.environ["RECV_EMAIL"]

def get_date_range():
    if len(sys.argv) == 3:
        from_date = sys.argv[1] + "0000"
        to_date   = sys.argv[2] + "2359"
        print(f"📅 조회 기간: {sys.argv[1]} ~ {sys.argv[2]}")
    elif len(sys.argv) == 2:
        from_date = sys.argv[1] + "0000"
        to_date   = sys.argv[1] + "2359"
        print(f"📅 조회 날짜: {sys.argv[1]}")
    else:
        now = datetime.now()
        from_date = (now - timedelta(hours=2)).strftime("%Y%m%d%H%M")
        to_date   = now.strftime("%Y%m%d%H%M")
        print(f"📅 조회 기간: 최근 2시간")
    return from_date, to_date

def fetch_bids(from_date, to_date):
    base_url = "https://apis.data.go.kr/1230000/ao/BidPublicInfoService/getBidPblancListInfoThng"

    params = {
        "serviceKey": API_KEY,
        "pageNo": "1",
        "numOfRows": "50",
        "inqryDiv": "1",
        "inqryBgnDt": from_date,
        "inqryEndDt": to_date,
        "type": "json",
    }

    # serviceKey는 URL 인코딩 없이 직접 붙이기
    query = urlencode({k: v for k, v in params.items() if k != "serviceKey"})
    url = f"{base_url}?serviceKey={API_KEY}&{query}"

    print(f"🌐 API 요청 URL (키 제외): {base_url}?serviceKey=***&{query}")

    try:
        res = requests.get(url, timeout=15)
        print(f"📡 응답 상태코드: {res.status_code}")
        print(f"📄 응답 내용 (앞 200자): {res.text[:200]}")

        data = res.json()
        items = data.get("response", {}).get("body", {}).get("items", [])
        if isinstance(items, dict):
            items = [items]
        return items if items else []
    except Exception as e:
        print(f"❌ API 호출 오류: {e}")
        return []

def send_email(bids, from_date, to_date):
    if not bids:
        print("새로운 입찰공고 없음 — 이메일 미발송")
        return

    period = f"{from_date[:8]} ~ {to_date[:8]}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = ""
    for b in bids:
        title  = b.get("bidNtceNm", "-")
        org    = b.get("ntceInsttNm", "-")
        amount = b.get("asignBdgtAmt", "-")
        end_dt = b.get("bidClseDt", "-")
        bid_no = b.get("bidNtceNo", "")
        link   = f"https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameTgong.do?bidNtceNo={bid_no}"

        rows += f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #eee;">
            <a href="{link}" style="color:#1a73e8;font-weight:bold;text-decoration:none;">{title}</a><br>
            <span style="color:#666;font-size:13px;">📌 {org}</span>
          </td>
          <td style="padding:10px;border-bottom:1px solid #eee;text-align:right;white-space:nowrap;">
            💰 {amount}원
          </td>
          <td style="padding:10px;border-bottom:1px solid #eee;text-align:center;white-space:nowrap;">
            ⏰ {end_dt}
          </td>
        </tr>
        """

    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:800px;margin:auto;">
      <h2 style="color:#1a73e8;">📋 나라장터 입찰공고 조회 결과</h2>
      <p>조회 기간: <b>{period}</b> | 총 <b>{len(bids)}건</b></p>
      <table width="100%" style="border-collapse:collapse;font-size:14px;">
        <thead>
          <tr style="background:#f1f3f4;">
            <th style="padding:10px;text-align:left;">공고명</th>
            <th style="padding:10px;text-align:right;">예산</th>
            <th style="padding:10px;text-align:center;">마감일시</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
      <p style="color:#999;font-size:12px;margin-top:20px;">발송 시각: {now_str} | GitHub Actions 자동 발송</p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[나라장터] 입찰공고 {len(bids)}건 ({period})"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = RECV_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PW)
            smtp.sendmail(GMAIL_ADDRESS, RECV_EMAIL, msg.as_string())
        print(f"✅ 이메일 발송 완료: {len(bids)}건")
    except Exception as e:
        print(f"❌ 이메일 발송 오류: {e}")

if __name__ == "__main__":
    from_date, to_date = get_date_range()
    print(f"🔍 나라장터 입찰공고 조회 중...")
    bids = fetch_bids(from_date, to_date)
    print(f"   → {len(bids)}건 조회됨")
    send_email(bids, from_date, to_date)
