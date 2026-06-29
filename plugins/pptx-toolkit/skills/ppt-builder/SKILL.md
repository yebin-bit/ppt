---
name: ppt-builder
description: >
  PowerPoint(.pptx) 덱을 만들거나 편집하는 작업의 **시작점이자 지휘자**. "PPT/슬라이드/덱/프레젠테이션
  만들어줘", "이 양식대로 OO별로 한 장씩", "템플릿 복제해서 값만 바꿔줘", "브랜드 색 맞춰 덱 만들어줘",
  "기존 pptx 수정해줘", "보고서 덱(경영계획/실적보고)" 같은 요청에 반드시 먼저 사용. 콘텐츠(차트 유무·
  반복 여부·템플릿 유무)를 보고 올바른 엔진으로 라우팅하고, 시작 시 (design.md + template.pptx) 한 쌍을
  갖추게 한다. 차트 든 양식 반복 → pptx-chart-template-filler, 브랜드 시스템 새 덱 → pptx-theme-engine,
  정적 편집/백지 일회성 → 공식 pptx 스킬로 위임. PPT가 조금이라도 관련되면(입력이든 출력이든) 이 스킬을
  먼저 떠올려 어떤 방식이 맞는지 판단할 것.
---

# PPT Builder (지휘자)

PPT 제작은 "어떤 엔진으로 만드느냐"가 결과의 비용·충실도·안정성을 좌우한다. 이 스킬은 **엔진을 직접
구현하지 않는다.** 대신 ① 시작 단계를 챙기고 ② 콘텐츠를 보고 올바른 경로로 보내고 ③ 함정을 미리 막는다.

연계 자산:
- 공식 `pptx` 스킬 — unpack/pack/add_slide/thumbnail/markitdown/soffice. 있으면 위임, 없으면 references의 폴백.
- `pptx-chart-template-filler` — 차트 든 양식 복제 + 값 교체(검증된 엔진).
- `pptx-theme-engine` — 토큰→마스터→테마화로 브랜드 시스템 위에 새 덱 생성.

## 3단계 워크플로

```
1단계 템플릿 설정 ──→ (design.md + template.pptx) 한 쌍
2단계 design.md 작성/정제 ──→ tokens.json · driver config 파생
3단계 엔진 결정트리 ──→ 생성/편집 ──→ QA(진짜 PowerPoint) ──→ gotchas 갱신
```

### 1단계 — 템플릿 설정
무엇으로 시작하든 끝나면 **design.md + template.pptx** 한 쌍이 남아야 한다. 시작점이 네 가지다:
- **case 1** 제대로 된 .pptx 마스터 → `pptx`에서 design.md를 *추출*. template = 원본.
- **case 2** 디자인만 된 .pptx → 예시 분석해 design.md + 대표 레이아웃을 template으로 승격.
- **case 3** 이미지/PDF 예시 → 시각 분석으로 design.md 초안 → template 제작.
- **case 4** 백지 → design.md 제안 → template 제작.

case 3·4는 **HTML 선행 디자인 승인 루프**를 권장(빠른 반복). 자세히는 `references/template-setup.md`,
`references/html-first-design.md`.

### 2단계 — design.md (사람이 쓰는 SSOT)
design.md가 디자인의 단일 출처다. 여기서 코드 입력물을 **파생**한다:
- design.md → `tokens.json` (theme-engine 입력: 색/폰트/타입스케일)
- design.md → driver config (chart-filler 입력: shape-id 맵·차트 좌표·캘리브레이션·데이터 스키마)

스캐폴드는 `templates/design.template.md`를 복사해 채운다. 섹션 구성·파생법은 `references/design-md-guide.md`.

### 3단계 — 엔진 결정트리
**콘텐츠를 먼저 본다.** 차트(네이티브)·내장엑셀·OLE가 있으면 복제 배관이 위험하므로 경로가 갈린다.

```
네이티브 차트/내장엑셀/OLE 있나?
├─ 없음(텍스트·도형·이미지만)
│   ├─ 기존 .pptx 편집/복제   → 공식 editing.md (unpack→add_slide.py→Edit→clean→pack)
│   └─ 브랜드 일관 새 덱       → pptx-theme-engine
├─ 있음 + 반복양식 + 값만 교체 → pptx-chart-template-filler  ★검증됨
├─ 백지 일회성(템플릿 없음)    → 공식 pptxgenjs.md
└─ 소량 + PowerPoint 앱 있음   → 앱에서 직접 "슬라이드 복제"(내장엔진이 차트 독립화) 후 숫자만 수정
```

비용 직관: 차트가 있고 장수가 많을수록 라이브러리가 배관을 자동 처리하는 경로(생성 또는 chart-filler)가
싸다. 정적이면 OOXML 복제가 싸다. 근거·라우팅 상세는 `references/engine-decision.md`.

## QA (필수)
- **항상 진짜 PowerPoint로 확인.** LibreOffice/soffice 렌더는 차트의 colors/style 공유 깨짐 같은
  "PowerPoint만 잡아내는" 문제를 **false-green**으로 통과시킨다.
- `markitdown`으로 내용 QA + placeholder grep(`xxxx|lorem|레이아웃`).
- 시각 QA는 fresh-eyes로(가능하면 서브에이전트). 겹침·오버플로우·정렬·여백(<0.5") 점검.

## 함정 (자세히는 references/gotchas.md — 새로 배우면 거기 누적)
차트 복제는 세 번 깨지며 확인된 것들이 있다: 차트는 묶음(chart+colors+style+rels) 통째 복제, 깨끗한
원본에서 복제, pack.py 우회, 외부엑셀 링크 제거, sldIdLst 등록. theme는 토큰 hex 고유·안전폰트.
공통으로 LibreOffice≠PowerPoint.

## 시작 체크리스트
1. 시작점이 case 1~4 중 무엇인가? → 1단계로 (design.md + template.pptx 확보)
2. design.md가 있나/충분한가? → 2단계로 (없으면 templates/design.template.md)
3. 슬라이드 콘텐츠가 무엇인가(차트/정적/반복)? → 3단계 결정트리로 엔진 선택
4. 생성/편집 후 → 진짜 PowerPoint QA → 새 함정은 gotchas.md에 기록
