# 10주 실습 — 교수 제공 코드 ② 최근 수치 표 + 기준금리와 네 지표의 시계열 차트
# 사용 = 차트 기능을 추가한 AI 코드가 두 번 고쳐도 동작하지 않을 때 이 코드로 실습을 이어 간다
# 실행 = IDLE: 이 파일과 지표 파일을 같은 폴더에 두고 F5 / Colab: 지표 파일을 올리고 셀에 붙여 넣어 실행
# 표준 라이브러리만 사용한다(설치할 패키지 없음). 차트는 HTML 안의 SVG 그림으로 그린다

import csv                     # CSV 파일을 읽는 표준 라이브러리
import html                    # HTML에 넣을 글자를 안전하게 바꾸는 표준 라이브러리
import os                      # 파일 경로를 다루는 표준 라이브러리
import pathlib                 # 파일 경로를 브라우저 주소로 바꾸는 표준 라이브러리
import webbrowser              # 만든 HTML 파일을 브라우저로 여는 표준 라이브러리

DEFAULT_FILE = "Week10_indicators.csv"   # Enter만 누르면 읽을 기본 지표 파일 이름
OUTPUT_FILE = "Week10_chart.html"        # 결과를 저장할 HTML 파일 이름

try:                                     # Colab에서 실행 중인지 확인한다
    import google.colab                  # Colab에만 있는 모듈
    IN_COLAB = True                      # 불러오기에 성공하면 Colab
except ImportError:                      # 모듈이 없으면
    IN_COLAB = False                     # IDLE 같은 내 컴퓨터 환경

try:                                     # 이 코드 파일이 있는 폴더를 찾는다
    BASE = os.path.dirname(os.path.abspath(__file__))   # IDLE에서는 코드 파일의 폴더
except NameError:                        # Colab 셀에는 코드 파일 경로가 없다
    BASE = os.getcwd()                   # Colab에서는 현재 폴더(/content)


def to_number(text):                     # 칸의 글자를 숫자로 바꾸는 함수
    text = text.strip()                  # 앞뒤 공백을 지운다
    if text == "":                       # 빈 칸이면
        return None                      # 값 없음(아직 발표되지 않은 달)
    return float(text)                   # 숫자로 바꾸어 돌려준다


def read_file(name):                     # 지표 파일을 읽는 함수
    path = os.path.join(BASE, name)      # 코드와 같은 폴더의 파일 경로
    with open(path, encoding="utf-8-sig", newline="") as f:   # BOM이 있는 UTF-8로 연다
        rows = list(csv.reader(f))       # 모든 행을 목록으로 읽는다
    header = rows[0]                     # 첫 행 = 열 이름
    data = rows[1:]                      # 둘째 행부터 = 한 달에 한 행
    return header, data                  # 열 이름과 자료를 돌려준다


def latest_values(header, data):         # 지표마다 최신 값과 한 달 전 값을 찾는 함수
    result = []                          # 결과를 담을 목록
    for col in range(1, len(header)):    # 연월 열(0번)을 뺀 나머지 지표 열마다
        points = [(row[0], to_number(row[col])) for row in data]   # (연월, 값) 목록
        points = [p for p in points if p[1] is not None]           # 빈 칸을 뺀다
        month, value = points[-1]        # 마지막 값 = 최신 값과 그 달
        prev_month, prev_value = points[-2]                        # 그 앞의 값
        unit = "원" if "(원)" in header[col] else "%p"              # 변화의 단위(환율 = 원, 나머지 = %p)
        result.append((header[col], month, value, prev_month, value - prev_value, unit))   # 한 행 추가
    return result                        # 지표별 결과를 돌려준다


def rate_change_months(data):            # 기준금리가 바뀐 달을 찾는 함수
    changes = []                         # 바뀐 달을 담을 목록
    for before, after in zip(data, data[1:]):          # 이웃한 두 달씩 비교한다
        if to_number(before[1]) != to_number(after[1]):    # 기준금리 값이 다르면
            changes.append((after[0], to_number(before[1]), to_number(after[1])))   # (달, 이전 값, 바뀐 값)
    return changes                       # 바뀐 달 목록을 돌려준다


def panel_svg(title, months, values, change_months, show_axis):   # 지표 하나의 선 그래프를 SVG로 그리는 함수
    width, height = 760, 130             # 그래프 한 칸의 크기(픽셀)
    left, right, top, bottom = 70, 20, 28, 22   # 안쪽 여백(왼쪽 = 세로축 숫자 자리)
    known = [v for v in values if v is not None]   # 빈 칸을 뺀 값
    low, high = min(known), max(known)   # 가장 작은 값과 가장 큰 값
    pad = (high - low) * 0.1 or 1        # 위아래 여유(값이 모두 같으면 1)
    low, high = low - pad, high + pad    # 여유를 더한 세로축 범위
    step = (width - left - right) / (len(months) - 1)   # 한 달의 가로 간격

    def x(i):                            # i번째 달의 가로 위치
        return left + i * step           # 왼쪽 여백 + 간격 × 순서

    def y(v):                            # 값 v의 세로 위치(위로 갈수록 큰 값)
        return top + (high - v) / (high - low) * (height - top - bottom)

    parts = [f"<svg width='{width}' height='{height}' style='display:block'>"]   # 그림 시작
    parts.append(f"<text x='{left}' y='16' font-size='14' font-weight='bold'>{html.escape(title)}</text>")   # 지표 이름
    parts.append(f"<rect x='{left}' y='{top}' width='{width - left - right}' height='{height - top - bottom}' fill='none' stroke='#ccc'/>")   # 테두리
    for v in (low + pad, high - pad):    # 세로축에 가장 작은 값과 가장 큰 값을 적는다
        parts.append(f"<text x='{left - 6}' y='{y(v) + 4:.1f}' font-size='11' text-anchor='end'>{v:,.2f}</text>")
    for month in change_months:          # 기준금리가 바뀐 달마다
        if month in months:              # 이 그래프의 기간 안이면
            i = months.index(month)      # 그 달의 순서
            parts.append(f"<line x1='{x(i):.1f}' y1='{top}' x2='{x(i):.1f}' y2='{height - bottom}' stroke='#d33' stroke-dasharray='4 3'/>")   # 붉은 점선
    segment = []                         # 빈 칸 없이 이어지는 점들
    for i, v in enumerate(values + [None]):   # 마지막에 None을 더해 남은 선을 마무리한다
        if v is None:                    # 빈 칸을 만나면
            if len(segment) > 1:         # 점이 두 개 이상 모였으면
                parts.append("<polyline fill='none' stroke='#0086CD' stroke-width='2' points='" + " ".join(segment) + "'/>")   # 선을 그린다
            segment = []                 # 다음 선을 새로 시작한다
        else:                            # 값이 있으면
            segment.append(f"{x(i):.1f},{y(v):.1f}")   # 점을 모은다
    if show_axis:                        # 맨 아래 그래프에만 가로축 글자를 적는다
        for i, month in enumerate(months):   # 달마다
            if month.endswith("-01") or month.endswith("-07"):   # 1월과 7월만 적는다
                parts.append(f"<text x='{x(i):.1f}' y='{height - 6}' font-size='11' text-anchor='middle'>{month}</text>")
    parts.append("</svg>")               # 그림 끝
    return "".join(parts)                # 하나의 SVG 글자로 돌려준다


def build_html(name, header, data, table, changes):   # 표와 차트를 HTML 문서로 만드는 함수
    months = [row[0] for row in data]    # 가로축 = 연월 목록
    change_months = [c[0] for c in changes]   # 기준금리가 바뀐 달
    lines = ["<html><head><meta charset='utf-8'><title>10주 지표 차트</title></head>"]   # 문서 머리
    lines.append("<body style='font-family:sans-serif'>")                              # 본문 시작
    lines.append(f"<h2>최근 수치 표 — {html.escape(name)}</h2>")                       # 제목(읽은 파일 이름)
    lines.append(f"<p>읽은 행 수 {len(data)}, 기간 {data[0][0]} ~ {data[-1][0]}</p>")   # 행 수와 기간
    lines.append("<table border='1' cellpadding='6' style='border-collapse:collapse'>")   # 표 시작
    lines.append("<tr><th>지표</th><th>최신 월</th><th>값</th><th>한 달 전 대비</th></tr>")   # 표 머리
    for label, month, value, prev_month, change, unit in table:                        # 지표마다
        lines.append(f"<tr><td>{html.escape(label)}</td><td>{month}</td><td>{value:,.2f}</td>"
                     f"<td>{change:+,.2f}{unit} ({prev_month} 대비)</td></tr>")         # 한 행씩 추가
    lines.append("</table>")                                                           # 표 끝
    lines.append("<h2>시계열 차트</h2>")                                               # 차트 제목
    lines.append("<p>붉은 점선 = 기준금리가 바뀐 달, 선이 끊긴 곳 = 아직 발표되지 않은 달</p>")   # 읽는 방법
    for col in range(1, len(header)):    # 지표마다 그래프 한 칸
        values = [to_number(row[col]) for row in data]                                 # 그 지표의 값 목록
        lines.append(panel_svg(header[col], months, values, change_months, col == len(header) - 1))   # 그래프 추가
    lines.append("</body></html>")       # 문서 끝
    return "\n".join(lines)              # 줄을 이어 하나의 문서로 돌려준다


def main():                              # 도구 전체를 실행하는 함수
    name = input(f"읽을 지표 파일 이름(Enter = {DEFAULT_FILE}): ").strip() or DEFAULT_FILE   # 파일 이름을 묻는다
    try:                                 # 파일 읽기를 시도한다
        header, data = read_file(name)   # 지표 파일을 읽는다
    except FileNotFoundError:            # 파일이 없으면
        print(f"오류: {name} 파일을 찾을 수 없습니다. 코드 파일과 같은 폴더에 있는지 확인합니다.")   # 원인 안내
        return                           # 도구를 끝낸다
    print("열 이름:", ", ".join(header)) # 열 이름을 출력한다
    print("읽은 행 수:", len(data))      # 읽은 행 수를 출력한다
    print("시작 월:", data[0][0], "/ 끝 월:", data[-1][0])   # 시작 월과 끝 월을 출력한다
    table = latest_values(header, data)  # 지표별 최신 값을 구한다
    print()                              # 빈 줄
    print("[최근 수치 표]")              # 표 제목
    for label, month, value, prev_month, change, unit in table:   # 지표마다
        print(f"- {label}: {month} {value:,.2f} (한 달 전 대비 {change:+,.2f}{unit})")   # 한 줄씩 출력
    changes = rate_change_months(data)   # 기준금리가 바뀐 달을 찾는다
    print()                              # 빈 줄
    print("[기준금리가 바뀐 달]")        # 목록 제목
    for month, before, after in changes: # 바뀐 달마다
        print(f"- {month}: {before:.2f} → {after:.2f}")   # 한 줄씩 출력
    page = build_html(name, header, data, table, changes)   # HTML 문서를 만든다
    if IN_COLAB:                         # Colab이면
        from IPython.display import HTML, display          # Colab의 화면 표시 기능
        display(HTML(page))              # 결과 칸에 바로 표시한다
    else:                                # IDLE 같은 내 컴퓨터 환경이면
        out = os.path.join(BASE, OUTPUT_FILE)               # 저장할 파일 경로
        with open(out, "w", encoding="utf-8") as f:         # HTML 파일을 쓴다
            f.write(page)                # 문서를 저장한다
        print("저장:", out)              # 저장 위치를 출력한다
        webbrowser.open(pathlib.Path(out).as_uri())         # 브라우저로 연다


main()                                   # 도구를 실행한다
