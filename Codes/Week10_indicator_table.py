# 10주 실습 — 교수 제공 코드 ① 지표 파일을 읽어 최근 수치 표를 만드는 도구
# 사용 = AI가 만든 코드가 두 번 고쳐도 동작하지 않을 때 이 코드로 실습을 이어 간다
# 실행 = IDLE: 이 파일과 지표 파일을 같은 폴더에 두고 F5 / Colab: 지표 파일을 올리고 셀에 붙여 넣어 실행
# 표준 라이브러리만 사용한다(설치할 패키지 없음)

import csv                     # CSV 파일을 읽는 표준 라이브러리
import html                    # HTML에 넣을 글자를 안전하게 바꾸는 표준 라이브러리
import os                      # 파일 경로를 다루는 표준 라이브러리
import pathlib                 # 파일 경로를 브라우저 주소로 바꾸는 표준 라이브러리
import webbrowser              # 만든 HTML 파일을 브라우저로 여는 표준 라이브러리

DEFAULT_FILE = "Week10_indicators.csv"   # Enter만 누르면 읽을 기본 지표 파일 이름
OUTPUT_FILE = "Week10_table.html"        # 결과를 저장할 HTML 파일 이름

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


def build_html(name, header, data, table):    # 결과를 HTML 문서로 만드는 함수
    lines = ["<html><head><meta charset='utf-8'><title>10주 최근 수치 표</title></head>"]   # 문서 머리
    lines.append("<body style='font-family:sans-serif'>")                                  # 본문 시작
    lines.append(f"<h2>최근 수치 표 — {html.escape(name)}</h2>")                           # 제목(읽은 파일 이름)
    lines.append(f"<p>읽은 행 수 {len(data)}, 기간 {data[0][0]} ~ {data[-1][0]}</p>")       # 행 수와 기간
    lines.append("<table border='1' cellpadding='6' style='border-collapse:collapse'>")    # 표 시작
    lines.append("<tr><th>지표</th><th>최신 월</th><th>값</th><th>한 달 전 대비</th></tr>")  # 표 머리
    for label, month, value, prev_month, change, unit in table:                            # 지표마다
        lines.append(f"<tr><td>{html.escape(label)}</td><td>{month}</td><td>{value:,.2f}</td>"
                     f"<td>{change:+,.2f}{unit} ({prev_month} 대비)</td></tr>")             # 한 행씩 추가
    lines.append("</table>")                                                               # 표 끝
    lines.append("<p>최신 월이 지표마다 다른 것은 발표 시점이 다르기 때문입니다(빈 칸 = 아직 발표되지 않은 달).</p>")   # 안내
    lines.append("</body></html>")                                                         # 문서 끝
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
    page = build_html(name, header, data, table)                  # HTML 문서를 만든다
    if IN_COLAB:                         # Colab이면
        from IPython.display import HTML, display                 # Colab의 화면 표시 기능
        display(HTML(page))              # 결과 칸에 바로 표시한다
    else:                                # IDLE 같은 내 컴퓨터 환경이면
        out = os.path.join(BASE, OUTPUT_FILE)                     # 저장할 파일 경로
        with open(out, "w", encoding="utf-8") as f:               # HTML 파일을 쓴다
            f.write(page)                # 문서를 저장한다
        print("저장:", out)              # 저장 위치를 출력한다
        webbrowser.open(pathlib.Path(out).as_uri())               # 브라우저로 연다


main()                                   # 도구를 실행한다
