# 1단계 — 템플릿 설정 (시작점별)

목표: **무엇으로 시작하든 끝나면 `design.md` + `template.pptx` 한 쌍이 남는다.**
design.md는 사람이 읽는 디자인 SSOT, template.pptx는 PowerPoint가 쓰는 바이너리 아티팩트다. 둘은 역할이
다르므로 항상 함께 둔다. 어느 쪽에서 시작하느냐(추출 vs 제작)만 케이스별로 다르다.

## case 1 — 제대로 된 .pptx 마스터 보유
방향: `pptx → design.md` **추출**. template.pptx = 원본 그대로.

1. `python -m markitdown template.pptx` 로 텍스트/구조 파악.
2. `python scripts/thumbnail.py template.pptx` 로 레이아웃 일람(공식 pptx 스킬).
3. `unpack.py` 후 `ppt/theme/theme1.xml`의 `clrScheme`·`fontScheme`, `slideMaster`/`slideLayout`을 읽어
   색 토큰·폰트·타입스케일·레이아웃을 design.md에 기록.
4. 편집/복제용으로 각 레이아웃 슬라이드의 shape `cNvPr id` 맵과 차트 프레임 좌표도 design.md에 적는다.

## case 2 — 디자인만 된 .pptx (마스터 없음)
예시 슬라이드는 예쁘지만 재사용 가능한 마스터/레이아웃이 없다.

1. markitdown + thumbnail로 어떤 "대표 레이아웃"들이 있는지 식별(표지/섹션/본문/데이터/마무리 등).
2. 그 색·폰트·간격을 design.md로 문서화.
3. template.pptx = 대표 레이아웃을 한 장씩 모은 "예시 슬라이드 덱"으로 정리(중복 제거, placeholder화).
   → 이후 3단계는 이 예시 슬라이드를 복제(add_slide.py 또는 chart-filler)해서 채운다.
   *주의*: 진짜 slideMaster 레이아웃이 아니라 "예시 슬라이드"다. 프로그램적으로 진짜 마스터를 만드는 건
   비싸므로, 예시 슬라이드 복제 방식으로 우회한다(이게 실무에서 잘 동작).

## case 3 — 이미지/PDF 예시만
1. 예시를 시각 분석해 색·폰트·레이아웃·간격을 추정 → design.md 초안.
2. template.pptx 제작: **HTML 선행 디자인 승인 루프**(`html-first-design.md`)로 디자인을 빠르게 확정한
   뒤 네이티브로 재구축하거나, 브랜드 시스템이 필요하면 `pptx-theme-engine`으로 토큰→마스터 생성.

## case 4 — 백지
1. 주제에 맞는 색 팔레트·타이포·모티프를 design.md로 제안(공식 pptx 스킬의 디자인 가이드 참고:
   주제 맞춤 팔레트, 한 색 지배, 다크/라이트 대비, 모티프 1개 반복).
2. 이후 case 3과 동일하게 HTML 루프 또는 theme-engine으로 template.pptx 제작.

## 산출물 점검
- [ ] design.md 존재 + 색토큰/타이포/레이아웃/(편집용)shape맵 채워짐
- [ ] template.pptx 존재 + PowerPoint에서 "복구" 없이 열림
- [ ] 둘이 일치(design.md의 색·폰트가 template과 같음)
