---
name: pptx-chart-template-filler
description: >
  네이티브 차트가 든 PowerPoint '양식(템플릿)' 한 장을 복제해서 항목(본부/부서/제품 등)별
  데이터만 갈아끼워 여러 장짜리 보고서를 만들 때 사용. 다음 상황에서 반드시 이 스킬을 사용:
  - "이 양식대로 OO별로 한 장씩 만들어줘", "템플릿 복제해서 값만 바꿔줘"
  - 경영계획/실적보고처럼 동일 레이아웃 + 차트가 반복되고 데이터만 다른 deck
  - 기존 .pptx의 차트(막대/달성률 등) 값을 본부별로 바꿔야 할 때
  genppt(코드로 새로 그리기)와 달리, 원본 양식을 그대로 복제하므로 폰트·차트 스타일 충실도가 높고
  PowerPoint에서 '복구' 없이 열린다. 차트를 도형으로 바꾸지 않고 진짜 편집 가능한 네이티브 차트를 유지.
---

# PPTX Chart Template Filler

## 무엇을 해결하나
PowerPoint 네이티브 차트는 단일 파일이 아니라 **묶음(bundle)** 이다:
`chart{N}.xml` + `colors{N}.xml` + `style{N}.xml` + `_rels`( + 임베디드 엑셀).
슬라이드를 복제할 때 이 묶음을 통째로 복제하고 모든 관계(rels)·`[Content_Types].xml`을
새 번호로 다시 이어주지 않으면, **PowerPoint가 "복구"하면서 슬라이드를 조용히 삭제**한다.
`add_slide.py`(pptx 스킬)는 슬라이드 껍데기만 복제하고 차트 묶음은 건드리지 않는다 — 이 스킬이 그 공백을 메운다.

## 워크플로
1. 양식 .pptx를 unpack (`pptx` 스킬의 `unpack.py`).
2. 양식 슬라이드의 shape `cNvPr id`와 차트 프레임 좌표를 파악 (한 번만; 양식별 config).
3. 항목마다: `clone_slide()` 로 슬라이드+차트묶음 복제 → `edit_chart()`/`set_text()`/`set_shape_y()` 로 값 주입.
4. `verify()` 로 무결성 확인 → `pack()` 로 zip.

## API (`scripts/pptx_template.py`)
- `clone_slide(unpacked, src='slide1.xml')` → `(새슬라이드명, {old_chart: new_chart})`.
  슬라이드가 참조하는 **모든 차트 묶음을 자동 복제**하고 rels/Content_Types/presentation 등록까지 처리.
  ⚠️ 항상 **편집 안 된 원본(master) 슬라이드**에서 복제할 것 (편집본에서 복제하면 값이 전파됨).
- `edit_chart(unpacked, chart_name, values, axis_max=None, major_unit=None)` — 캐시값·축 수정, externalData 제거.
- `set_chart_categories(unpacked, chart_name, cats)` — 카테고리 라벨 변경(구성/추이형 차트용).
- `set_text(dom, shape_id, lines)` — 조각난 run을 깨끗한 단일 run으로 재작성(문단별 스타일 보존).
- `set_run_by_marker(dom, shape_id, marker, new_text)` — marker(예 '%') 포함 run만 교체.
- `set_shape_y / set_shape_x(dom, shape_id, emu)` — 달성률 선/박스 등 위치 이동.
- `load(path)/save(dom,path)` — 슬라이드 XML 열고 저장.
- `verify(unpacked)` → 끊긴 rels·미등록 파트 목록(빈 리스트면 정상).
- `pack(unpacked, out)` — `[Content_Types].xml`을 먼저 넣어 zip. **pack.py 대신 이걸 쓴다**(아래 함정 3).

## 함정 체크리스트 (세 번 깨지며 확인됨)
1. **묶음 전체 복제**: 차트 본체만 복제하고 colors/style을 공유하면 PowerPoint가 복구→슬라이드 삭제.
   `clone_slide`는 차트마다 colors/style을 독립 복제한다.
2. **원본에서 복제**: 이미 값을 넣은 슬라이드를 복제하면 그 값이 전파됨. 항상 깨끗한 master에서 복제.
3. **pack.py 우회**: 차트의 MS 벤더 확장(c15/c16)을 pack.py가 "빈 요소"로 오탐 → 검증 실패.
   원본에도 있는 정상 구조이므로 `pack()`(수동 zip)으로 묶는다.
4. **외부 엑셀 링크 제거**: 양식 차트가 `file://` 사내 경로를 참조하면 끊긴 링크. `edit_chart`가 자동 제거.
5. **sldIdLst 등록**: 새 슬라이드는 `presentation.xml`의 `<p:sldIdLst>`에도 들어가야 함(`clone_slide`가 처리).

## 예시
`scripts/build_ch4.py` 가 키움 ch4 양식용 driver 예시(= 양식별 config: shape-id 맵 + 달성률 캘리브레이션 + 데이터 `ch4_data.py`).
새 양식에 적용하려면 이 driver를 복사해서 shape id·좌표·데이터만 바꾸면 된다.
실행: `python scripts/build_ch4.py <unpacked_template_dir> <out.pptx>`
