# 7주 실습 5 예시 코드 — KOSIS 가구주 연령 20~29세의 1인 가구 수 조회(2025년 · 전국)
# 표준 라이브러리만 사용한다 — Colab에서 따로 설치할 것이 없다
import json                              # 응답(JSON 문자열)을 파이썬 자료로 바꾸는 모듈
import urllib.parse                      # 요청 조건을 웹 주소 형식으로 바꾸는 모듈
import urllib.request                    # 웹 주소로 요청을 보내는 모듈
from google.colab import userdata        # Colab 보안 비밀을 읽는 모듈

# ── 조회 조건 ─────────────────────────────────────────────
API_KEY = userdata.get("KOSIS_KEY")      # 보안 비밀에 'KOSIS_KEY'로 저장한 인증키(코드에 키 값이 남지 않는다)
ORG_ID, TBL_ID = "101", "DT_1JC1511"     # 기관 ID와 통계표 ID: 가구주의 연령 및 가구원수별 가구(일반가구) - 시군구
ITEM = "T210"                            # 항목 코드: T210 = 1인 가구
REGION = "00"                            # 행정구역 코드: 00 = 전국
AGES = ["025", "030"]                    # 가구주 연령 코드: 025 = 20~24세 · 030 = 25~29세
YEAR = "2025"                            # 기준 연도(연 단위 통계)

# 요청 조건을 묶는다 — 코드가 여러 개이면 「+」로 이어 붙인다
params = {                               # 요청 조건 묶음(이름: 값)
    "method": "getList",                 # 기능: 통계자료 조회
    "apiKey": API_KEY,                   # 인증키
    "format": "json",                    # 응답 형식: JSON
    "jsonVD": "Y",                       # JSON 응답의 표준 형식 사용
    "orgId": ORG_ID,                     # 기관 ID
    "tblId": TBL_ID,                     # 통계표 ID
    "itmId": ITEM,                       # 항목 코드
    "objL1": REGION,                     # 첫째 분류: 행정구역
    "objL2": "+".join(AGES),             # 둘째 분류: 가구주 연령(025+030)
    "prdSe": "Y",                        # 주기: Y = 연
    "startPrdDe": YEAR,                  # 시작 연도
    "endPrdDe": YEAR,                    # 끝 연도
}                                        # 요청 조건 묶음 끝
url = ("https://kosis.kr/openapi/Param/statisticsParameterData.do?"   # 통계자료 조회 주소
       + urllib.parse.urlencode(params))                              # 조건을 주소 뒤에 붙인다

with urllib.request.urlopen(url, timeout=30) as resp:   # 요청을 보내고 응답을 받는다
    data = json.loads(resp.read().decode("utf-8"))      # 응답 본문을 파이썬 자료로 바꾼다

if isinstance(data, dict):                              # 오류 응답은 목록이 아니라 err·errMsg를 담은 자료로 온다
    print("오류 코드:", data.get("err"))                # 예: 11(인증키) · 21(요청 변수) · 30(데이터 없음)
    print("오류 메시지:", data.get("errMsg"))           # 예: 잘못된 요청 변수를 호출 하였습니다.
else:                                                   # 정상 응답은 행의 목록으로 온다
    print("요청 조건:", TBL_ID, "/ 항목", ITEM, "/ 행정구역", REGION,          # 요청한 통계표·항목·행정구역
          "/ 가구주 연령", "+".join(AGES), "/", YEAR)                         # 요청한 연령 코드·연도
    print("받은 행 수:", len(data), "/ 요청한 연령 코드 수:", len(AGES))       # 두 수가 같아야 한다
    total = 0                                                                 # 세그먼트 값(두 연령의 합)을 담을 변수
    for r in data:                                                            # 받은 행을 하나씩 꺼내
        print(r["C1_NM"], "|", r["C2_NM"], "|", r["ITM_NM"], "|",             # 행정구역·가구주 연령·항목 이름
              r["DT"], r["UNIT_NM"], "|", r["PRD_DE"])                        # 값·단위·연도
        total += int(r["DT"])                                                 # 값(문자열)을 정수로 바꾸어 더한다
    print("세그먼트 값(가구주 연령 20~29세의 1인 가구):", total, data[0]["UNIT_NM"],  # 두 연령의 합과 단위
          "/ 기준 연도", data[0]["PRD_DE"])                                       # 기준 연도
