import requests
import smtplib
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# ─────────────────────────────────────────
# GitHub Secrets에서 자동으로 불러옵니다
# ─────────────────────────────────────────
API_KEY       = os.environ["NARAJANGTER_API_KEY"]
GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PW  = os.environ["GMAIL_APP_PASSWORD"]
RECV_EMAIL    = os.environ["RECV_EMAIL"]

# ─────────────────────────────────────────
# 나라장터 API 호출
# ─────────────────────────────────────────
def fetch_bids():
    url = "http://apis.data.go.kr/1230000/ao/BidPublicInfoService/getBidPblancListInfoThng"
    
    # 오늘 날짜 기준으로 조회
    today = datetime.now()
    from_date = (today - timedelta(hours=2)).strftime("%Y%m%d%H%M")
    to_date   = today.strftime("%Y%m%d%H%M")

    params = {
        "serviceKey": API_KEY,
        "pageNo": "1",
        "numOfRows": "20",
        "inqryDiv": "1",
        "inqryBgnDt": from_date,
        "inqryEndDt": to_date,
        "type": "json",
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        items = data.get("response", {}).get("body", {}).get("items", [])
        if isinstance(items, dict):
            items = [items]
        return items if items else []
    except Exception as e:
        print(f"API 호출 오류: {e}")
        return []

# ─────────────────────────────────────────
# Gmail 이메일 발송
# ─────────────────────────────────────────
def send_email(bids):
    if not bids:
        print("새로운 입찰공고 없음 — 이메일 미발송")
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # HTML 이메일 본문 작성
    rows = ""
    for b in bids:
        title   = b.get("bidNtceNm", "-")
        org     = b.get("ntceInsttNm", "-")
        amount  = b.get("asignBdgtAmt", "-")
        end_dt  = b.get("bidClseDt", "-")
        bid_no  = b.get("bidNtceNo", "")
        link    = f"https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameTgong.do?bidNtceNo={bid_no}"

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
      <h2 style="color:#1a73e8;">📋 나라장터 새 입찰공고 ({now_str})</h2>
      <p>총 <b>{len(bids)}건</b>의 새 입찰공고가 있습니다.</p>
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
      <p style="color:#999;font-size:12px;margin-top:20px;">
        이 메일은 GitHub Actions에 의해 자동 발송되었습니다.
      </p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[나라장터] 새 입찰공고 {len(bids)}건 ({now_str})"
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

# ─────────────────────────────────────────
# 실행
# ─────────────────────────────────────────
if __name__ == "__main__":
    print(f"🔍 나라장터 입찰공고 조회 중... ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    bids = fetch_bids()
    print(f"   → {len(bids)}건 조회됨")
    send_email(bids)
