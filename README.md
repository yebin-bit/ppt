# ppt — PowerPoint 제작 스킬 마켓플레이스

PowerPoint(.pptx) 덱을 **시작 단계부터 엔진 선택까지** 일관되게 만드는 Claude Code 스킬 모음.

## 설치

```
/plugin marketplace add yebin-bit/ppt
/plugin install pptx-toolkit
```

## 구성: `pptx-toolkit` 플러그인

| 스킬 | 역할 |
|---|---|
| **ppt-builder** | 지휘자. ① 템플릿 설정(→ `design.md` + `template.pptx`) ② design.md(SSOT) ③ 콘텐츠 보고 엔진 결정트리로 라우팅 + 진짜 PowerPoint QA. 함정(gotchas) 누적. |
| **pptx-chart-template-filler** | 네이티브 차트가 든 양식 한 장을 복제해 항목별 데이터만 교체. 차트 묶음(chart+colors+style+rels) 자동 복제·재연결. |
| **pptx-theme-engine** | 토큰(`tokens.json`)→마스터(`gen.js`)→테마화(`themeify.py`). 색/폰트를 한곳에서 제어, 테마색 하나로 전체 리컬러. |

공식 Anthropic `pptx` 스킬과 함께 쓴다(unpack/pack/add_slide/thumbnail/markitdown/soffice). 있으면 위임, 없으면 폴백.

## 핵심 아이디어

- **design.md(사람) + template.pptx(바이너리) 한 쌍**을 항상 갖춘다. design.md에서 tokens.json·driver를 파생.
- **엔진은 콘텐츠로 결정**: 차트+반복양식+값교체 → chart-filler / 브랜드 새 덱 → theme-engine / 정적 편집·일회성 → 공식 pptx.
- **QA는 반드시 진짜 PowerPoint** — LibreOffice는 차트 공유 깨짐을 false-green으로 통과시킨다.

자세한 설계는 `plugins/pptx-toolkit/skills/ppt-builder/DESIGN.md`.
