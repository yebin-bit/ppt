# gotchas — 살아있는 함정 로그

PPT 자동화에서 실제로 깨지며 알아낸 함정들. **새로 배우면 여기에 누적**한다(날짜·증상·원인·해결).

## 차트 복제 (chart-filler에서 세 번 깨지며 확인)
1. **차트 = 묶음 전체 복제** — chart 본체만 복제하고 `colors{N}.xml`/`style{N}.xml`을 원본과 공유하면,
   PowerPoint가 "차트마다 자기 색상/스타일 파트를 가져야 한다" 규칙으로 **복구하며 슬라이드를 조용히 삭제**.
   *증상*: LibreOffice는 전 슬라이드 정상, **PowerPoint는 1장만** 뜸. *해결*: colors/style까지 차트별 독립 복제
   (`clone_slide`가 처리).
2. **깨끗한 원본(master)에서 복제** — 이미 값을 넣은 슬라이드를 복제하면 그 값이 전파됨.
   *증상*: 모든 장이 동일 라벨(예: 전부 "100.8%"). *해결*: 항상 편집 안 된 master에서 복제 후 값 주입.
3. **pack.py 우회** — 복제 차트의 MS 벤더 확장(`c15`/`c16`, `<c:ext>`)을 pack.py 검증기가 "빈 요소"로
   **오탐(false-positive)**. 원본에도 있는 정상 구조. *해결*: `[Content_Types].xml`을 먼저 넣어 수동 zip
   (`pptx_template.pack()`).
4. **외부 엑셀 링크 제거** — 양식 차트가 `file://` 사내 경로(externalData)를 참조하면 끊긴 링크.
   *해결*: `edit_chart`가 externalData 자동 제거.
5. **sldIdLst 수동 등록** — `add_slide.py`는 추가할 `<p:sldId>` 줄을 출력만 함 → 직접 삽입해야 함.
   안 넣으면 슬라이드가 목록에 없어 안 보임. (`clone_slide`가 자동 처리.)

## 테마 (theme-engine)
6. **토큰 hex 고유** — 색 토큰끼리 hex가 겹치면 srgb→schemeClr 매핑이 모호해져 캐스케이드가 꼬임.
7. **안전폰트 권장** — QA(LibreOffice) 폰트 치환 때문. 최종 충실도는 PowerPoint에서 확인.

## 공통
8. **LibreOffice ≠ PowerPoint** — soffice 렌더가 통과해도 PowerPoint에서 깨질 수 있다(특히 차트 공유,
   벤더 확장, 폰트). **최종 검증은 반드시 진짜 PowerPoint.** "복구하시겠습니까?" 메시지가 뜨면 실패 신호.
9. **placeholder 잔존** — 템플릿 복제 후 `xxxx`/`lorem`/"이 슬라이드 레이아웃" 류 텍스트가 남음.
   *해결*: `markitdown out.pptx | grep -iE "xxxx|lorem|레이아웃"` 으로 점검.
10. **슬롯 ≠ 항목 수** — 템플릿에 4칸인데 데이터가 3개면, 4번째 그룹(이미지+텍스트박스)을 **통째로 삭제**.
    텍스트만 비우면 빈 도형이 남는다.

---
### 새 함정 추가 양식
```
N. **제목** — 증상 / 원인 / 해결. (발견일 YYYY-MM-DD, 어떤 양식/작업에서)
```
