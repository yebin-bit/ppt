# ppt-builder — 설계 문서 (spec)

- 작성일: 2026-06-29
- 상태: 설계 확정 대기(사용자 리뷰)
- 작성자: 박예빈 + Claude

## 1. 목적 / 문제

Anthropic 공개 `pptx` 스킬은 강력하지만, 실제 반복 업무(키움 경영계획·실적보고 등)에서 다음이 빠져 있어 매번 헤맸다:

- **시작 단계 부재**: "템플릿이 *있다*"고 가정. 임의의 .pptx / 예시 이미지 / HTML 디자인에서 **템플릿을 만들어내는** 흐름이 없음.
- **디자인 SSOT 부재**: 색/폰트/레이아웃이 그때그때. 사람이 읽고 고치는 단일 출처(design.md)가 없음.
- **엔진 선택 가이드 부재**: 차트가 든 슬라이드를 복제할 때 공식 `add_slide.py`는 차트 묶음을 복제하지 않아 PowerPoint가 슬라이드를 조용히 삭제하는 등, "언제 생성 vs 언제 복제"를 판단하는 레이어가 없음.

이 스킬은 **이미 보유한 두 엔진 스킬을 묶고 시작 단계를 더하는 "지휘자(orchestrator)"** 다. 새 엔진 코드를 거의 만들지 않는다.

## 2. 보유 자산 (참조/호출 대상)

| 자산 | 정체 | 역할 |
|---|---|---|
| 공식 `pptx` 스킬 | unpack/pack/add_slide/thumbnail/markitdown + editing.md + pptxgenjs.md | 베이스 메커니즘. 있으면 위임, 없으면 폴백 |
| `pptx-chart-template-filler` | `pptx_template.py`(차트묶음 자동복제·verify·pack우회) + driver 예시 + 함정 체크리스트 | **"반복양식+차트+값교체"** 경로 엔진 |
| `pptx-theme-engine` | `tokens.json` → `gen.js`(마스터) → `themeify.py`(srgb→schemeClr 캐스케이드) | **"브랜드 시스템 우선 새 덱 생성"** 경로 엔진 |

설계 원칙: **두 엔진을 복제(fork)하지 않고 참조/호출.** 공식 스킬은 "있으면 사용, 없으면 폴백"(하이브리드).

## 3. 목표 / 비목표

목표
- 무엇으로 시작하든 1단계가 끝나면 **(design.md + template.pptx)** 한 쌍이 갖춰진다.
- 3단계에서 **콘텐츠를 보고 올바른 엔진으로 라우팅**한다.
- 시행착오를 **gotchas.md에 누적**한다.

비목표
- 새 차트복제/테마 엔진을 다시 구현하지 않음(기존 스킬 재사용).
- 임의 디자인의 픽셀 단위 완벽 재현(특히 HTML→PPT는 승인용 근사).
- 공식 pptx 스킬이 이미 잘 하는 정적 편집/QA 메커니즘 재작성.

## 4. 아키텍처: 3단계 파이프라인 + 엔진 결정트리

```
1단계 템플릿 설정 ──→ (design.md + template.pptx)
2단계 design.md 작성/정제 ──→ tokens.json · driver config 파생
3단계 엔진 결정트리 ──→ 생성/편집 ──→ QA(진짜 PowerPoint)
                                   └─→ gotchas.md 갱신
```

### 4.1 1단계 — 템플릿 설정 (시작점별)

목표: 끝나면 항상 `design.md` + `template.pptx` 한 쌍.

- **case 1 — 제대로 된 .pptx 마스터 보유**: `pptx → design.md` *추출*. 마스터/레이아웃/테마색·폰트를 읽어 design.md로 문서화. template.pptx = 원본.
- **case 2 — 디자인만 된 .pptx**: 마스터 없음. 예시 슬라이드를 분석해 design.md 작성 + 대표 레이아웃을 정리해 template.pptx(예시 슬라이드 모음)로 승격.
- **case 3 — 이미지/PDF 예시**: 시각 분석으로 design.md 초안 → template.pptx 제작(아래 HTML 루프 또는 theme-engine).
- **case 4 — 백지**: design.md를 새로 제안 → template.pptx 제작.

**HTML 선행 디자인 승인 루프(case 3/4, 선택)**: 빠른 반복을 위해 HTML로 1차 디자인 → 사용자 승인 → 그 결과를 design.md에 고정 → template.pptx 제작(네이티브 재구축). HTML은 **승인 도구**일 뿐 최종 변환기가 아니다(편집성·안정성 위해 네이티브 재구축).

### 4.2 2단계 — design.md (사람이 쓰는 SSOT)

design.md는 **마스터 문서**이고, 여기서 코드 입력물을 **파생**한다:

- `design.md` → `tokens.json` (theme-engine 입력: 색/폰트/타입스케일)
- `design.md` → driver config (chart-filler 입력: shape-id 맵·차트 좌표·캘리브레이션·데이터 스키마)

design.md 권장 섹션(기본 제공 후 수정):
1. **색 토큰** — ink/bg/primary/secondary/accent/surface/muted (고유 hex, 겹치지 않게 — theme-engine 캐스케이드 요구).
2. **타이포** — head/body 폰트, 타입스케일(title/section/body/caption pt).
3. **레이아웃 패턴** — 마스터별(COVER/SECTION/CONTENT/DATA/CLOSING) 구조.
4. **양식 매핑(편집/복제용)** — shape `cNvPr id` 맵, 차트 프레임 좌표, 달성률 등 캘리브레이션.
5. **규칙** — 스트라이프/언더라인 금지, 텍스트박스 margin 0, 대비, 안전폰트(QA 신뢰도).

### 4.3 3단계 — 엔진 결정트리 (라우팅)

```
슬라이드에 네이티브 차트/내장엑셀/OLE 있나?
├─ 없음(텍스트·도형·이미지만)
│   ├─ 기존 .pptx 편집/복제   → 공식 editing.md (unpack→add_slide.py→Edit→clean→pack)
│   └─ 브랜드 일관 새 덱       → pptx-theme-engine (tokens→마스터→themeify)
├─ 있음 + 반복양식 + 값만 교체 → pptx-chart-template-filler (clone_slide→edit_chart…→verify→pack)  ★검증됨
├─ 백지 일회성(템플릿 없음)    → 공식 pptxgenjs.md
└─ 소량 + PowerPoint 앱 있음   → 앱에서 직접 "슬라이드 복제"(내장엔진이 차트 독립화 자동) 후 숫자만 수정
```

**비용 직관**: 차트가 있고 장수가 많을수록 생성형(라이브러리가 배관 자동) 또는 chart-filler가 유리. 정적이면 OOXML 복제가 싸다.

**QA(필수)**: 항상 **진짜 PowerPoint**로 확인. LibreOffice/soffice 렌더는 차트 colors/style 공유 깨짐을 **false-green**으로 통과시킴. 추가로 `markitdown` 내용 QA + placeholder grep(`xxxx|lorem|레이아웃`).

## 5. gotchas.md (살아있는 함정 로그) — 시드

차트복제(chart-filler에서 세 번 깨지며 확인):
1. **차트=묶음 전체 복제**: chart 본체만 복제하고 colors/style 공유 → PowerPoint 복구하며 슬라이드 삭제.
2. **깨끗한 원본(master)에서 복제**: 편집본에서 복제하면 값이 전파됨.
3. **pack.py 우회**: c15/c16 벤더확장을 "빈 요소"로 오탐 → 수동 zip(`pack()`).
4. **외부 엑셀 링크 제거**: `file://` 사내 경로 참조 → 끊김. `edit_chart`가 자동 제거.
5. **sldIdLst 수동 등록**: add_slide.py는 줄만 출력 → 직접 삽입(`clone_slide`가 처리).

테마(theme-engine):
6. **토큰 hex 고유**: 색끼리 hex 겹치면 srgb→schemeClr 매핑 모호.
7. **안전폰트 권장**: QA(LibreOffice) 폰트 치환 때문. 최종은 PowerPoint 확인.

공통:
8. **LibreOffice ≠ PowerPoint**: 렌더 통과해도 PowerPoint에서 깨질 수 있음(특히 차트). 최종 검증은 PowerPoint.

## 6. 스킬 파일 구성

```
ppt-builder/
├─ SKILL.md                  # 3단계 흐름 + 엔진 결정트리 + QA. 짧게, 나머지는 references로 점진공개
├─ DESIGN.md                 # (이 문서)
├─ references/
│   ├─ template-setup.md     # case 1~4 → design.md+template.pptx
│   ├─ html-first-design.md  # HTML 승인 루프
│   ├─ design-md-guide.md    # design.md 작성법 + tokens.json/driver 파생법
│   ├─ engine-decision.md    # 결정트리 상세 + 비용 근거 + 라우팅 대상 스킬
│   └─ gotchas.md            # 살아있는 함정 로그(위 시드)
└─ templates/
    └─ design.template.md    # design.md 스캐폴드(기본 제공 → 수정)
```

엔진 스크립트(`pptx_template.py`, `gen.js`, `themeify.py`)는 **이 스킬에 복제하지 않고** 두 엔진 스킬을 `~/.claude/skills/`에 함께 설치해 참조.

## 7. 의존성 / 설치

- `~/.claude/skills/`에 함께 설치: `ppt-builder`, `pptx-chart-template-filler`, `pptx-theme-engine`.
- 공식 `pptx` 스킬: 있으면 unpack/pack/add_slide/thumbnail/markitdown/soffice 위임, 없으면 references에 최소 폴백 안내.
- 런타임: python(defusedxml), node(pptxgenjs), (QA용) soffice — references에 명시.

## 8. 미해결 / 향후

- design.md → tokens.json 자동 파생을 스크립트로 만들지(권장) vs 수기 매핑.
- 레퍼런스 덱 역분석(이미지→토큰/마스터)은 theme-engine의 미구현 영역 — best-effort, 후순위.
- chart-filler driver 자동 생성(shape-id 맵 자동 탐색) 개선 여지.
