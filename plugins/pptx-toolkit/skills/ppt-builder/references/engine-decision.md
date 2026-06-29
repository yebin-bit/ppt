# 엔진 결정트리 — 상세 + 근거

PPT 제작의 핵심 판단은 "어떤 엔진으로 만드느냐"다. 콘텐츠(특히 네이티브 차트 유무)와 반복성, 템플릿
유무가 비용·충실도·안정성을 좌우한다.

## 결정트리
```
네이티브 차트 / 내장엑셀 / OLE 가 슬라이드에 있나?
├─ 없음 (텍스트·도형·이미지만)
│   ├─ 기존 .pptx를 편집하거나 정적 슬라이드 복제 → 공식 pptx 스킬 editing.md
│   │     unpack.py → (필요시) add_slide.py → Edit로 내용 → clean.py → pack.py
│   └─ 일관된 브랜드 룩의 새 덱을 시스템으로     → pptx-theme-engine
│         tokens.json → gen.js(마스터) → themeify.py(srgb→schemeClr 캐스케이드)
├─ 있음 + 동일 레이아웃 반복 + 데이터만 교체     → pptx-chart-template-filler  ★실무 검증됨
│         clone_slide(차트묶음 자동복제) → edit_chart/set_text/set_shape_y → verify → pack
├─ 백지에서 일회성 새 덱 (템플릿 없음)           → 공식 pptx 스킬 pptxgenjs.md
└─ 소량(예: 3~5장) + 손에 PowerPoint 앱 있음     → 앱에서 직접 "슬라이드 복제" 후 숫자만 수동 수정
        (PowerPoint 내장 엔진이 차트 묶음 독립화를 자동 처리. 장수 많으면 수동 편집이 부담)
```

## 왜 차트에서 갈리나 (핵심 근거)
PowerPoint 네이티브 차트는 단일 파일이 아니라 **묶음**: `chart{N}.xml` + `colors{N}.xml` + `style{N}.xml`
+ `_rels` (+ 내장 엑셀). 슬라이드를 복제하면 슬라이드의 "쪽지(rId)"만 복사돼 **두 슬라이드가 같은 차트를
가리킨다** → 한쪽 데이터를 바꾸면 둘 다 바뀐다. 진짜 독립시키려면 묶음 전체를 새 번호로 복제하고
`[Content_Types].xml`·rels·`sldIdLst`를 다시 엮어야 한다.

- 공식 `add_slide.py`는 **슬라이드 껍데기까지만** 복제하고 차트 묶음은 안 건드린다 → 차트 양식엔 부족.
- `pptx-chart-template-filler`가 정확히 그 공백(묶음 복제·재연결)을 메운다.
- 생성형(pptxgenjs/theme-engine)은 라이브러리가 배관(파트 생성·고유 ID·Content_Types·colors/style 분리)을
  자동 처리 → 장수가 늘어도 "한 번 짜고 한 번 실행". 단, 원본 양식의 폰트·차트 스타일을 다시 그리는
  근사라 충실도는 복제보다 낮을 수 있다.

## 비용·충실도·안정성 요약
| 경로 | 비용(장수↑) | 충실도(원본 그대로) | 안정성(PowerPoint) |
|---|---|---|---|
| chart-filler(복제) | 중(배관 코드가 처리) | 높음(원본 복제) | 높음(검증됨) |
| theme-engine(생성) | 낮음(자동) | 중(재구축 근사) | 중(폰트/차트 재검증 필요) |
| 공식 editing(정적) | 낮음 | 높음 | 높음 |
| PowerPoint 앱 수동 | 장수에 비례(수동) | 최고 | 최고 |

## 판단 한 줄
- 같은 양식 + 차트 + 값만 반복 → **chart-filler**.
- 브랜드 시스템으로 새로 + 나중에 색/폰트 일괄 변경 → **theme-engine**.
- 기존 덱 텍스트/이미지 손보기 → **공식 editing**.
- 한두 번 일회성 → **pptxgenjs** 또는 PowerPoint 앱.
