# design.md 작성 가이드 (사람이 쓰는 SSOT)

design.md는 디자인 결정의 **단일 출처**다. 매번 OOXML을 파싱하지 않고 이 파일만 보면 색·폰트·레이아웃·
양식 매핑을 알 수 있어야 한다. 그리고 여기서 코드 입력물을 **파생**한다.

## 파생 관계
```
design.md (사람)
 ├─→ tokens.json        (pptx-theme-engine 입력)  : color/font/typeScale
 └─→ driver config      (pptx-chart-template-filler 입력) : shape-id 맵·차트 좌표·캘리브레이션·데이터 스키마
```
원칙: **design.md를 고치고, 거기서 tokens.json / driver를 다시 만든다.** 코드 산출물을 직접 손대지 말 것
(틀어진다). 자동 파생 스크립트가 있으면 그걸 쓰고, 없으면 design.md를 보고 수기로 채운다.

## 섹션 구성 (templates/design.template.md 스캐폴드)
1. **색 토큰** — `ink / bg / primary / secondary / accent / surface / muted`. 각 토큰 **고유 hex**
   (겹치면 theme-engine의 srgb→schemeClr 매핑이 모호해진다). 한 색이 지배(60–70%)하도록.
2. **타이포** — `head`/`body` 폰트(PPT 실재 폰트), 타입스케일: title 36–44 / section 20–24 / body 14–16 /
   caption 10–12 pt.
3. **레이아웃 패턴** — 마스터별 구조(COVER/SECTION/CONTENT/DATA/CLOSING): 배경·제목 위치·placeholder 배치.
4. **양식 매핑(편집·복제용)** — 슬라이드별 shape `cNvPr id`(예: 43=제목, 20=요약, 54=달성률박스),
   차트 프레임 좌표, 달성률 선 등 캘리브레이션 값, 차트 카테고리/계열 스키마.
5. **규칙** — 언더라인/장식 사선 금지, 텍스트박스 margin 0, 최소 대비, 안전폰트, 여백 ≥0.5".

## tokens.json 파생 예 (theme-engine)
design.md 색 토큰을 그대로 옮긴다:
```json
{ "color": { "ink":"#1F2937", "bg":"#FFFFFF", "primary":"#C62828",
             "secondary":"#1A1A2E", "accent":"#E53935", "surface":"#F6F7F8", "muted":"#9CA3AF" },
  "font": { "head":"Cambria", "body":"Calibri" },
  "typeScale": { "title":40, "section":22, "body":15, "caption":11 } }
```

## driver config 파생 예 (chart-filler)
design.md "양식 매핑"을 driver(예: build_<form>.py + <form>_data.py)로 옮긴다. shape id·좌표는 양식 전용,
라이브러리(pptx_template.py)는 그대로 재사용. 자세한 API는 pptx-chart-template-filler/SKILL.md.

## 주의
- shape id·좌표·캘리브레이션은 **양식 전용** 값이라 design.md(또는 driver)에만 두고, 절대 라이브러리
  코드에 박지 않는다 — 다른 양식에서 안 맞는다.
- design.md는 사람이 읽으니 표·주석을 적극 사용. "키움행=레드", "1위만 강조" 같은 규칙도 글로 남긴다.
