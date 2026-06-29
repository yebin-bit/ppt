# <프로젝트/양식 이름> — design.md

> 디자인 SSOT. 이 파일을 고치고, 여기서 tokens.json(theme-engine) / driver(chart-filler)를 파생한다.
> 코드 산출물을 직접 손대지 말 것.

## 1. 색 토큰 (각 고유 hex)
| 토큰 | hex | 용도 |
|---|---|---|
| ink | #1F2937 | 본문 텍스트 |
| bg | #FFFFFF | 기본 배경 |
| primary | #______ | 지배색(60–70%) |
| secondary | #______ | 보조색 |
| accent | #______ | 강조 포인트(소량) |
| surface | #______ | 카드/패널 배경 |
| muted | #9CA3AF | 캡션/보조 텍스트 |

## 2. 타이포
- head 폰트: ______ (PPT 실재 폰트)
- body 폰트: ______
- 타입스케일(pt): title 40 / section 22 / body 15 / caption 11

## 3. 레이아웃 패턴 (마스터별)
- COVER: ______
- SECTION: ______
- CONTENT: ______ (예: 2단 텍스트+그림)
- DATA: ______ (예: 큰 숫자 콜아웃 / 차트)
- CLOSING: ______

## 4. 양식 매핑 (편집·복제용 — 차트/복제 양식일 때)
- 슬라이드 shape id 맵: 43=제목, 20=요약, 54=... (cNvPr id)
- 차트 프레임 좌표(EMU): chartA=(x,y,cx,cy), ...
- 캘리브레이션: 달성률 선 y=수식/값, ...
- 차트 데이터 스키마: 카테고리 [...], 계열 [...]

## 5. 규칙
- 언더라인/장식 사선 남발 금지(AI 티). 텍스트박스 margin 0. 대비 확보. 여백 ≥0.5".
- 한 색 지배 + 보조 1–2 + 강조 1. 토큰 hex 겹치지 않기.
- (양식별 규칙) 예: "키움 행은 강조색", "1위만 강조" 등.

## 6. 파생물
- tokens.json: 위 1·2 → theme-engine 입력
- driver: 위 4 → chart-filler driver(build_<form>.py + <form>_data.py)
