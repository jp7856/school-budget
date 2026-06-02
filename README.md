# 📋 나라장터 입찰공고 Gmail 알림

나라장터 새 입찰공고를 자동으로 Gmail로 받아보는 시스템입니다.
GitHub Actions를 사용하므로 **서버 비용이 전혀 없습니다.**

---

## 📁 파일 구조

```
narajangter/
├── check_bids.py                        # 메인 실행 스크립트
└── .github/
    └── workflows/
        └── narajangter.yml              # 자동 실행 스케줄
```

---

## ⚙️ 설정 방법 (최초 1회)

### 1단계 — 이 저장소를 GitHub에 업로드
- GitHub에서 새 Repository 만들기 (이름: `narajangter`)
- 파일 2개 업로드:
  - `check_bids.py`
  - `.github/workflows/narajangter.yml`

### 2단계 — GitHub Secrets 등록
Repository → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름           | 입력값                        |
|-----------------------|-------------------------------|
| `NARAJANGTER_API_KEY` | 나라장터 API 인증키            |
| `GMAIL_ADDRESS`       | 발신 Gmail 주소               |
| `GMAIL_APP_PASSWORD`  | Gmail 앱 비밀번호 (16자리)    |
| `RECV_EMAIL`          | 수신 이메일 주소              |

### 3단계 — 테스트 실행
- Repository → **Actions 탭** → `나라장터 입찰공고 알림` → **Run workflow**

---

## ⏰ 실행 스케줄

| 실행 시각 (한국시간) | 요일   |
|---------------------|--------|
| 오전 9시            | 월~금  |
| 오후 1시            | 월~금  |
| 오후 5시            | 월~금  |

---

## 📧 이메일 예시

제목: `[나라장터] 새 입찰공고 5건 (2026-06-01 09:00)`

본문에 공고명, 기관명, 예산, 마감일시, 바로가기 링크가 포함됩니다.


