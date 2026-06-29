---
name: pptx-theme-engine
description: >
  브랜드 디자인 시스템(색 토큰·폰트·타입스케일 + 슬라이드 마스터/레이아웃)을 먼저 만들고,
  그 위에서 모든 슬라이드를 생성하는 PowerPoint 제작 방식. Anthropic 공개 `pptx` 스킬과 함께 쓴다
  (unpack/pack/soffice/thumbnail/QA 그대로 사용). 다음 상황에서 사용:
  - 일관된 브랜드 룩의 여러 장짜리 덱을 만들 때
  - "나중에 색/폰트를 한 번에 바꾸고 싶다", "테마만 바꿔서 재활용" 요구가 있을 때
  - 슬라이드마다 색을 하드코딩(slide-maker)하지 않고 토큰 한 곳에서 제어하고 싶을 때
  핵심 차이: 기본 pptx 스킬의 "처음부터 생성"은 슬라이드별 수작업이라 나중에 일괄 변경이 불가.
  이 엔진은 토큰→마스터→슬라이드 순으로 지어서, 토큰(또는 PowerPoint 테마색) 하나만 바꾸면 전체가 리컬러된다.
---

# PPTX Theme Engine

기본 `pptx` 스킬 위에 얹는 **세 번째 제작 경로**. (`editing.md`=템플릿 편집, `pptxgenjs.md`=슬라이드별 생성, 이 스킬=시스템 우선 생성)

## 철학
빈 캔버스에 페이지마다 스타일을 박는 디자이너 vs. 브랜드 툴킷(색 토큰·폰트·마스터)을 먼저 짓고 그 위에 페이지를 얹는 디자이너. 둘 다 예쁠 수 있지만, **변수 하나로 전체를 재구성**할 수 있는 건 후자뿐이다. 대부분의 AI 도구는 색을 슬라이드마다 srgb로 박아 이 단계를 건너뛴다.

## 3단계 워크플로
1. **토큰 정의** — `tokens.json`: 색(ink/bg/primary/secondary/accent/surface/muted) + 폰트(head/body) + 타입스케일.
2. **시스템 위에 생성** — `gen.js`(pptxgenjs): `defineSlideMaster`로 마스터들(COVER/SECTION/CONTENT/DATA/CLOSING)을 **토큰만 참조**해 정의하고, 모든 슬라이드를 `addSlide({masterName})` + placeholder로 만든다. 구조적 룩(배경·제목·placeholder)은 마스터에 산다.
3. **테마화(핵심)** — `themeify.py`: 생성된 덱을 unpack 후
   - `theme1.xml`의 `clrScheme`(accent1~6 등) · `fontScheme`에 토큰을 심고
   - 슬라이드/마스터/레이아웃의 하드코딩 `srgbClr`(토큰 hex)를 **`schemeClr` 참조**로 치환
   → 결과 덱은 **PowerPoint에서 테마색 하나만 바꿔도 전체가 리컬러**된다(진짜 캐스케이드).

## 실행
```bash
node scripts/gen.js tokens.json deck.pptx          # 시스템 위에 덱 생성
python scripts/themeify.py deck.pptx tokens.json themed.pptx   # 테마 심고 schemeClr 치환
# QA·렌더는 기본 pptx 스킬 그대로:
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf themed.pptx
```
색/폰트만 바꾸려면 `tokens.json` 수정 후 위 2줄 재실행. 또는 `themed.pptx`를 PowerPoint에서 열어 테마색을 바꾸면 즉시 전체 적용.

## 캐스케이드 원리 (왜 되나)
슬라이드가 색을 `<a:schemeClr val="accent1"/>`로 **참조**하면, 그 값은 마스터의 `clrMap`을 거쳐 `theme1.xml`의 accent1로 해석된다. 그래서 theme의 accent1 한 값만 바꿔도 accent1을 참조하는 모든 요소(배경·숫자·아이콘·카드 헤더…)가 동시에 바뀐다. `themeify.py`가 하는 일이 바로 "srgb 하드코딩 → schemeClr 참조"로 바꿔 이 연결을 만드는 것.

## 규칙 / 주의
- 토큰 색끼리 **hex가 겹치면** schemeClr 매핑이 모호해진다 — 토큰마다 고유 hex 사용.
- 기본 pptx 스킬의 디자인 가이드 준수: **스트라이프/언더라인 금지**, 텍스트박스 margin 0, 대비 확보.
- 폰트는 안전 폰트(Calibri/Cambria/Arial 등) 권장 — QA(LibreOffice) 신뢰도 때문.
- 충실도 한계: LibreOffice 미리보기는 폰트 치환이 있으니 최종은 PowerPoint에서 확인.

## 다음 단계(미구현, best-effort 영역)
**레퍼런스 덱 역분석**: 마음에 드는 덱 이미지 + 브랜드 사양을 받아 레이아웃/간격/타입스케일을 추출해 토큰·마스터로 환원. 비전+휴리스틱이라 "닮은 청사진" 수준이며, 위 토큰 스키마로 출력하면 이 엔진에 그대로 연결된다.
