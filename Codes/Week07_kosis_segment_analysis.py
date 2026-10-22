# 7주 실습 5 심화 예시 코드 — 세그먼트 분석 3종(추세 · 지역 · 연령 비교)과 인사이트 그래프
# 세그먼트 = 가구주 연령 20~29세의 1인 가구 · 통계표 = KOSIS DT_1JC1511(가구주의 연령 및 가구원수별 가구)
import json                                   # 응답(JSON 문자열)을 파이썬 자료로 바꾸는 모듈
import urllib.parse                           # 요청 조건을 웹 주소 형식으로 바꾸는 모듈
import urllib.request                         # 웹 주소로 요청을 보내고 파일을 내려받는 모듈
import matplotlib.pyplot as plt               # 그래프를 그리는 모듈
from matplotlib import font_manager           # 글꼴을 등록하는 모듈
from google.colab import userdata             # Colab 보안 비밀을 읽는 모듈

# ── 한글 글꼴 준비(Colab 기본 글꼴에는 한글이 없다) ─────────────────
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"  # 나눔고딕 글꼴 파일 주소
urllib.request.urlretrieve(FONT_URL, "NanumGothic.ttf")         # 글꼴 파일을 Colab 작업 폴더에 내려받는다
font_manager.fontManager.addfont("NanumGothic.ttf")             # 내려받은 글꼴을 matplotlib에 등록한다
plt.rcParams["font.family"] = "NanumGothic"                     # 그래프 글꼴을 나눔고딕으로 정한다
plt.rcParams["axes.unicode_minus"] = False                      # 음수 기호가 깨지지 않게 한다

# ── 공통 조건 ─────────────────────────────────────────────
API_KEY = userdata.get("KOSIS_KEY")           # 보안 비밀에 저장한 인증키(코드에 키 값이 남지 않는다)
URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do?"  # KOSIS 통계자료 조회 주소
SEG = ["025", "030"]                          # 세그먼트의 가구주 연령 코드: 20~24세 · 25~29세
ACCENT, DARK, LIGHT = "#0086CD", "#5F6B73", "#B8C0C6"  # 강조색(세그먼트) · 짙은 회색 · 옅은 회색


def fetch(items, regions, ages, start, end):  # 조건에 맞는 행을 받아 오는 함수
    params = {                                # 요청 조건 묶음(이름: 값)
        "method": "getList", "apiKey": API_KEY, "format": "json", "jsonVD": "Y",  # 기능 · 인증키 · 응답 형식
        "orgId": "101", "tblId": "DT_1JC1511",  # 기관 ID · 통계표 ID
        "itmId": items, "objL1": regions, "objL2": ages,  # 항목 · 행정구역 · 가구주 연령(여러 개는 +로 연결)
        "prdSe": "Y", "startPrdDe": start, "endPrdDe": end,  # 연 단위 · 시작 연도 · 끝 연도
    }                                         # 요청 조건 묶음 끝
    with urllib.request.urlopen(URL + urllib.parse.urlencode(params), timeout=60) as resp:  # 요청을 보낸다
        data = json.loads(resp.read().decode("utf-8"))  # 응답을 파이썬 자료로 바꾼다
    if isinstance(data, dict):                # 오류 응답은 err·errMsg를 담은 자료로 온다
        raise RuntimeError(f"KOSIS 오류 {data.get('err')}: {data.get('errMsg')}")  # 오류 내용을 보여 주고 멈춘다
    print("받은 행 수:", len(data))            # 받은 행 수를 출력한다
    return data                               # 받은 행 목록을 돌려준다


def total(rows, item, region=None, ages=None, year=None):  # 조건에 맞는 행의 값을 더하는 함수
    s = 0                                     # 합계를 담을 변수
    for r in rows:                            # 받은 행을 하나씩 확인한다
        if r["ITM_ID"] != item:               # 항목이 다르면 건너뛴다
            continue                          # 다음 행으로
        if region is not None and r["C1"] != region:  # 행정구역이 다르면 건너뛴다
            continue                          # 다음 행으로
        if ages is not None and r["C2"] not in ages:  # 가구주 연령이 다르면 건너뛴다
            continue                          # 다음 행으로
        if year is not None and r["PRD_DE"] != year:  # 연도가 다르면 건너뛴다
            continue                          # 다음 행으로
        s += int(r["DT"])                     # 값(문자열)을 정수로 바꾸어 더한다
    return s                                  # 합계를 돌려준다


def tidy(ax):                                 # 그래프의 테두리와 격자를 정리하는 함수
    ax.spines[["top", "right"]].set_visible(False)  # 위쪽 · 오른쪽 테두리를 없앤다
    ax.grid(axis="y", color="#E3E7EA", linewidth=0.8)  # 옅은 가로 격자만 둔다
    ax.set_axisbelow(True)                    # 격자를 그래프 아래에 그린다


# ── 5-2 추세: 세그먼트는 시장보다 빨리 커지는가 ───────────────────────
rows = fetch("T210+T100", "00", "000+" + "+".join(SEG), "2015", "2025")  # 2015~2025 전국 · 1인 가구와 일반가구
years = [str(y) for y in range(2015, 2026)]   # 연도 목록
seg = [total(rows, "T210", "00", SEG, y) for y in years]      # 세그먼트(가구주 20대 1인 가구) 규모
one = [total(rows, "T210", "00", ["000"], y) for y in years]  # 전체 1인 가구 규모
gen = [total(rows, "T100", "00", ["000"], y) for y in years]  # 전체 일반가구 규모
idx = lambda v: [x / v[0] * 100 for x in v]    # 2015년을 100으로 두고 바꾸는 계산
cagr = (seg[-1] / seg[0]) ** (1 / 10) - 1      # 세그먼트의 연평균 증가율(10년)
fig, ax = plt.subplots(figsize=(8, 4.5))       # 그래프 영역을 만든다
for vals, name, color, lw in [(gen, "일반가구", LIGHT, 2), (one, "전체 1인 가구", DARK, 2), (seg, "세그먼트(가구주 20대 1인 가구)", ACCENT, 3)]:  # 세 선을 차례로
    ax.plot(years, idx(vals), color=color, linewidth=lw, marker="o", markersize=5)  # 지수 선을 그린다
    ax.annotate(f"{name} {idx(vals)[-1]:.0f}", (years[-1], idx(vals)[-1]), xytext=(6, 0), textcoords="offset points", va="center", color="#2B3238", fontsize=9)  # 선 끝에 이름과 값을 직접 적는다
ax.axhline(100, color="#9AA3A9", linewidth=0.8, linestyle="--")  # 2015년 기준선(100)
peak = seg.index(max(seg))                     # 세그먼트가 가장 컸던 해의 위치
if peak < len(seg) - 1:                        # 정점이 마지막 해가 아니면(최근 감소)
    head = f"세그먼트는 {years[peak]}년 정점 뒤 {seg[-1] / seg[peak] - 1:+.1%} — 같은 기간 전체 1인 가구 {one[-1] / one[peak] - 1:+.1%}"  # 정점 이후 변화
else:                                          # 계속 증가했으면
    head = f"세그먼트는 10년간 {seg[-1] / seg[0]:.2f}배(연평균 {cagr:.1%}) — 일반가구는 {gen[-1] / gen[0]:.2f}배"  # 10년 증가
ax.set_title(head, loc="left", fontsize=12)    # 인사이트를 제목으로
ax.set_ylabel("2015년 = 100")                  # 세로축 이름
tidy(ax)                                      # 테두리 · 격자 정리
ax.set_xlim(-0.3, len(years) + 2.5)           # 오른쪽 이름 표시 공간을 남긴다
plt.tight_layout()                            # 여백을 맞춘다
plt.show()                                    # 그래프를 화면에 표시한다
print(f"[5-2] 세그먼트 {seg[0]:,} → {seg[-1]:,}가구 · 연평균 {cagr:.1%} · 정점 {years[peak]}년 {seg[peak]:,}가구 · 일반가구 {gen[0]:,} → {gen[-1]:,}가구")  # 수치 근거를 출력한다

# ── 5-3 지역: 세그먼트가 많고 몰려 있는 지역은 어디인가 ─────────────────
REG = {"11": "서울", "21": "부산", "22": "대구", "23": "인천", "24": "광주", "25": "대전", "26": "울산", "29": "세종",  # 시도 코드(앞줄)
       "31": "경기", "32": "강원", "33": "충북", "34": "충남", "35": "전북", "36": "전남", "37": "경북", "38": "경남", "39": "제주"}  # 시도 코드와 이름
rows = fetch("T210+T100", "00+" + "+".join(REG), "000+" + "+".join(SEG), "2025", "2025")  # 2025년 전국과 17개 시도
nat = total(rows, "T210", "00", SEG) / total(rows, "T100", "00", ["000"]) * 100  # 전국 비중(세그먼트 ÷ 일반가구)
pts = []                                      # 지역별 결과를 담을 목록
for code, name in REG.items():                # 시도를 하나씩
    s = total(rows, "T210", code, SEG)         # 그 지역의 세그먼트 규모
    g = total(rows, "T100", code, ["000"])     # 그 지역의 일반가구 수
    pts.append((name, s / 10000, s / g * 100))  # (이름, 규모[만 가구], 비중[%])를 담는다
mid = sorted(p[1] for p in pts)[len(pts) // 2]  # 지역 규모의 중앙값(세로 기준선)
big = {n for n, s, r in sorted(pts, key=lambda p: -p[1])[:2]}  # 규모 상위 2개 지역
dense = {n for n, s, r in sorted(pts, key=lambda p: -p[2])[:3]}  # 비중 상위 3개 지역
fig, ax = plt.subplots(figsize=(8, 5.5))       # 그래프 영역을 만든다
for name, s, r in pts:                         # 지역을 하나씩 점으로
    hot = s >= mid and r >= nat                # 규모도 크고 비중도 전국보다 높은 지역인가
    ax.scatter(s, r, s=90, color=ACCENT if hot else LIGHT, edgecolor="white", linewidth=1.5, zorder=3)  # 점을 찍는다
    if hot or name in big or name in dense:    # 강조 지역과 각 축의 상위 지역에만
        ax.annotate(name, (s, r), xytext=(5, 4), textcoords="offset points", fontsize=9, color="#2B3238" if hot else "#7A848B")  # 지역 이름을 붙인다
ax.axhline(nat, color="#9AA3A9", linewidth=0.8, linestyle="--")  # 전국 비중 기준선
ax.axvline(mid, color="#9AA3A9", linewidth=0.8, linestyle="--")  # 규모 중앙값 기준선
hot_names = [n for n, s, r in pts if s >= mid and r >= nat]  # 오른쪽 위(규모 · 비중 모두 높은) 지역
ax.set_title(f"규모가 크고 집중된 지역: {' · '.join(hot_names)}", loc="left", fontsize=12)  # 인사이트를 제목으로
ax.set_xlabel("세그먼트 규모(만 가구)")          # 가로축 이름
ax.set_ylabel("지역 일반가구 중 세그먼트 비중(%)")  # 세로축 이름
tidy(ax)                                      # 테두리 · 격자 정리
plt.tight_layout()                            # 여백을 맞춘다
plt.show()                                    # 그래프를 화면에 표시한다
print(f"[5-3] 전국 비중 {nat:.1f}% · 규모 중앙값 {mid:.1f}만 가구")  # 기준선 값을 출력한다
for name, s, r in sorted(pts, key=lambda p: -p[2]):  # 17개 지역 전체를 비중 순서로
    print(f"[5-3] {name}: {s:.1f}만 가구 · 비중 {r:.1f}%")  # 수치 근거로 출력한다

# ── 5-4 연령 비교: 왜 이 세그먼트인가 ─────────────────────────────
AGES = {"020": "15~19", "025": "20~24", "030": "25~29", "035": "30~34", "040": "35~39", "045": "40~44", "050": "45~49",  # 연령 코드(앞줄)
        "055": "50~54", "060": "55~59", "065": "60~64", "070": "65~69", "075": "70~74", "080": "75~79", "085": "80~84", "086": "85+"}  # 연령 코드와 이름
rows = fetch("T210+T100", "00", "+".join(AGES), "2025", "2025")  # 2025년 전국 · 연령대별
cnt = [total(rows, "T210", "00", [c]) / 10000 for c in AGES]       # 연령대별 1인 가구 수(만 가구)
shr = [total(rows, "T210", "00", [c]) / total(rows, "T100", "00", [c]) * 100 for c in AGES]  # 연령대별 1인 가구 비중(%)
colors = [ACCENT if c in SEG else LIGHT for c in AGES]  # 세그먼트 연령만 강조색
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=False)  # 두 그래프를 나란히(축 하나씩)
for ax, vals, title, unit in [(axes[0], cnt, "1인 가구 수", "만 가구"), (axes[1], shr, "가구주 연령대 가구 중 1인 가구 비중", "%")]:  # 수와 비중을 차례로
    ax.bar(list(AGES.values()), vals, color=colors, width=0.8)  # 막대를 그린다
    ax.set_title(title, loc="left", fontsize=11)  # 그래프 이름
    ax.set_ylabel(unit)                       # 세로축 단위
    ax.tick_params(axis="x", rotation=60, labelsize=8)  # 연령 이름을 기울여 표시한다
    tidy(ax)                                  # 테두리 · 격자 정리
    for i, c in enumerate(AGES):              # 세그먼트 막대에만
        if c in SEG:                          # 값을 직접 적는다
            ax.annotate(f"{vals[i]:.0f}" if unit == "%" else f"{vals[i]:.1f}", (i, vals[i]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8)  # 막대 위 값
rank = sorted(range(len(shr)), key=lambda i: -shr[i])  # 비중이 높은 순서
most = list(AGES.values())[cnt.index(max(cnt))]  # 1인 가구 수가 가장 많은 연령대
seg_share = total(rows, "T210", "00", SEG) / total(rows, "T100", "00", SEG) * 100  # 가구주 20대 가구 중 1인 가구 비중
fig.suptitle(f"가구주 20대 가구의 {seg_share:.0f}%가 1인 가구 — 1인 가구 수는 {most}세가 가장 많음", x=0.01, ha="left", fontsize=12)  # 인사이트를 제목으로
plt.tight_layout()                            # 여백을 맞춘다
plt.show()                                    # 그래프를 화면에 표시한다
for i, c in enumerate(AGES):                   # 세그먼트 연령의
    if c in SEG:                              # 수치를
        print(f"[5-4] {AGES[c]}세: 1인 가구 {cnt[i]:.1f}만 · 비중 {shr[i]:.1f}% · 비중 순위 {rank.index(i) + 1}/{len(AGES)}")  # 근거로 출력한다
