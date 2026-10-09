# 6주 실습 5 예시 코드 — ECOS 기준금리 최근 3년 분기 값 조회
# 표준 라이브러리만 사용한다 — Colab에서 따로 설치할 것이 없다
import json                      # 응답(JSON 문자열)을 파이썬 자료로 바꾸는 모듈
import urllib.request            # 웹 주소로 요청을 보내는 모듈

# ── 조회 조건 ─────────────────────────────────────────────
API_KEY = "sample"               # 한국은행이 공개한 시험용 인증키(가입 불필요 · 1회 최대 10건)
STAT_CODE = "722Y001"            # 통계표 코드: 1.3.1. 한국은행 기준금리 및 여수신금리
ITEM_CODE = "0101000"            # 항목 코드: 한국은행 기준금리
CYCLE = "Q"                      # 주기: Q = 분기
START, END = "2023Q4", "2026Q3"  # 조회 기간: 최근 3년(12개 분기)


def fetch(first, last):          # first번째부터 last번째까지 요청하는 함수
    # 요청 주소 = 서비스명/인증키/형식/언어/시작 번호/끝 번호/통계표/주기/시작 시점/끝 시점/항목
    url = (f"https://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/json/kr/"   # 서비스·키·형식·언어
           f"{first}/{last}/{STAT_CODE}/{CYCLE}/{START}/{END}/{ITEM_CODE}")    # 번호·통계표·주기·기간·항목
    with urllib.request.urlopen(url, timeout=30) as resp:   # 요청을 보내고 응답을 받는다
        data = json.loads(resp.read().decode("utf-8"))      # 응답 본문을 파이썬 자료로 바꾼다
    if "StatisticSearch" not in data:                       # 정상 응답에만 이 키가 있다
        result = data.get("RESULT", {})                     # 오류 응답은 RESULT에 코드와 메시지를 담는다
        print("오류 코드:", result.get("CODE"))               # 예: ERROR-301
        print("오류 메시지:", result.get("MESSAGE"))          # 예: sample은 최대 10건 이내에서 …
        return None, []                                     # 총 건수 없음 · 빈 목록을 돌려준다
    body = data["StatisticSearch"]                          # 정상 응답의 본문
    return body["list_total_count"], body["row"]            # 총 건수와 받은 행 목록을 돌려준다


total, rows1 = fetch(1, 10)      # 1차 요청: 1~10번
_, rows2 = fetch(11, 20)         # 2차 요청: 11~20번(남은 건수만 온다)
rows = rows1 + rows2             # 두 번 받은 행을 하나로 합친다

print("응답의 총 건수:", total)                                   # 조건에 맞는 전체 건수
print("받은 행 수:", len(rows1), "+", len(rows2), "=", len(rows))  # 실제로 받은 행 수
print("총 건수와 받은 행 수가 같은가:", total == len(rows))        # 같지 않으면 누락이 있다
for r in rows:                                                     # 받은 행을 하나씩 꺼내
    print(r["ITEM_NAME1"], r["TIME"], r["DATA_VALUE"], r["UNIT_NAME"])  # 통계 이름·시점·값·단위를 출력한다
