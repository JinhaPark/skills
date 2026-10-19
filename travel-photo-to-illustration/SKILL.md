---
name: travel-photo-to-illustration
description: Clean travel photographs, convert them to watercolor or colored-pencil illustrations, optimize responsive WebP assets, and integrate them into existing travel guides. Use for 여행 사진 수채화·워터칼러·색연필화 변환, 차창 반사광·전봇대·전선·하단 단체관광객·군중 제거, 사진 상단 보완, 모바일 최적화, or guide image batches. Preserve portrait subjects, architectural details and natural water reflections. Delegate visual edits to the built-in imagegen skill and use the bundled script only for resizing and encoding.
---

# Travel Photo to Illustration

사용자 지시를 우선하고 한국어 존댓말로 결과를 설명하라. 기존 그림과 완료된 작업을 재사용하라. 실제 승인 범위에서 완료하고 별도 승인 규칙을 임의로 만들지 말라.

## 1. 입력과 현재 상태

- 적용 가능한 `AGENTS.md`, 최신 기본 브랜치·작업 브랜치·PR·감사 기록을 확인하라. 가이드 작업에는 [guide-integration.md](references/guide-integration.md)를 읽어라. 일반 이미지 편집에는 저장소 작업을 요구하지 말라.
- 원본을 직접 열어 파일명, EXIF 방향 적용 크기, 장소·피사체, 편집 대상/스타일 참고 역할, 제거·보존 요소를 기록하라. 파일 순서·이름·업로드 시각으로 장소나 촬영일을 확정하지 말라.
- 사용자 여행 사진과 인터넷 캡처를 구분하라. 외부 사진의 원본 페이지·저작자·이용 조건을 확인하고 필수 크레딧·라이선스·수정 표시를 충족하라. 화풍 변환을 이용 허가의 대체로 취급하지 말라. 권리 미확인 캡처는 공개하지 말고 재사용 가능한 대체 사진을 확보하라.
- 건물 식별을 원본 특징과 사용자 정정에 대조하라. 미노르·구르에미르를 비비하눔으로 잘못 배치했던 정정을 반영하라. 다른 PR에서 완료한 그림은 재작업하지 말라.

## 2. 정리와 화풍 계획

[editing-rules.md](references/editing-rules.md)를 읽고 각 사진의 짧은 제거 목록·보존 목록을 만들라. 여러 장이면 원본↔결과 대응을 유지하라.

- 차창/창문 반사·전봇대·전선·우발적 하단 군중을 정리하라. 인물 중심 사진의 주인공, 조각상과 그 손, 실제 수면 반영은 보존하라.
- 기존 그림1–2점에 맞춰 절제된 투명 수채화와 섬세한 색연필 선을 사용하라. 풍경은 수채화, 건축·유물 세부는 색연필화를 기본 선택으로 삼되 기존 화풍을 우선하라.
- 표·숫자·지도·전시 패널은 의미가 바뀌지 않도록 `documentary-photo`로 유지하라.
- 원본 구도·비율·원근·주요 건축을 유지하라. 크롭·상단 복원·하늘 확장은 요청되었을 때만 수행하고 범위와 생성 보완 부분을 기록하라.

## 3. 시각 편집

- 현재 제공되는 **imagegen 스킬**을 읽고 내장 이미지 도구를 사용하라. 로컬 원본과 참고 이미지는 먼저 뷰어로 확인하라. 현재 도구가 제공하는 파일 경로/대화 이미지 참조 방식을 따르고 인자를 추측하지 말라.
- 정리와 화풍 변환을 한 요청에 합칠 수 있으면 합쳐라. [editing-rules.md](references/editing-rules.md)의 프롬프트에 실제 삭제·보존 요소만 넣어라.
- 결과를 원본과 비교하라. 군중 잔여물·주인공 훼손·잘린 탑·비율 변형·창/문양 변경·가짜 문자·뒤틀린 반영을 검사하고 필요한 부분만 재편집하라. 승인된 자산과 원본을 덮어쓰지 말라.
- 도구 실패 시 임의로 API/CLI나 Pillow 필터로 시각 편집을 대체하지 말고 imagegen 스킬의 대체 경로 규칙을 따르라.

## 4. 모바일 자산

최종 생성 파일의 로컬 경로를 확보하라. 프로젝트 참조 자산을 기본 생성 위치에만 남겨두지 말라. 아래 Python/Pillow 스크립트는 **시각 편집 없이** EXIF 방향 적용·리사이즈·WebP 인코딩·메타데이터 제거만 수행한다. 명령의 스크립트 경로는 이 스킬 폴더 기준이다.

아이폰 HEIC/HEIF 원본은 설치된 `pillow-heif`가 있으면 지원한다. 코덱이 없으면 사용 가능한 변환 도구로 방향·색상·크기를 보존해 PNG/JPEG 작업 사본을 만들고 원본과의 대응을 기록하라. 확장자만 바꾸거나 원본을 덮어쓰지 말라.

```bash
python scripts/optimize-images.py \
  --input /absolute/path/final-illustration.png \
  --source /absolute/path/original.jpeg \
  --id city-subject-watercolor --style watercolor \
  --out-dir /absolute/path/project/public/illustrations
```

- `--style`: `watercolor`, `colored-pencil`, `documentary-photo`. 기본 폭 후보480/800/1200px, 파일당 상한**250,000bytes**. 원본·생성본·지정한 기존 편집본 양축을 넘기지 말라. 작은 원본에는 가능한 최대 폭을 추가하며 업스케일하지 않는다.
- 기존 그림 재편집에는 `--edit-input /path/previous-edit.png`를 추가하라. 요청된 구도 확장은 `--framing outpaint`, 크롭은 `--framing crop`으로 명시하라. 기본 `preserve`는 비율 오차0.3% 이상을 거부한다. 검사를 피하려고 원본 크기를 바꾸거나 framing 옵션을 임의 사용하지 말라.
- JSON 출력의 `audit`는 감사 문서로 분리하고 manifest에는 필요한 필드만 옮겨라. 범용 `framingEdit: outpaint/crop`은 프로젝트의 좁은 예외를 자동 충족하지 않는다.
- 기존 파일은 기본적으로 덮어쓰지 않는다. 승인된 교체에만 `--overwrite`를 사용하라. 품질 하한에서도 예산 초과라면 실패 원인을 해결하고 검사를 끄지 말라.

## 5. 통합과 완료

- 가이드 작업은 [guide-integration.md](references/guide-integration.md)에 따라 manifest·한글 캡션·alt·단일 배치·필수 출처 표시를 갱신하라. 원본 JPEG/HEIC·생성 PNG·사적 로컬 경로를 공개 커밋하지 말라.
- 실제 디코딩·크기·비율·용량·메타데이터·중복을 검사하고 모바일 캡션·넘침·srcset·오프라인 동작을 확인하라. 데스크톱 에뮬레이션과 실제 iPhone 테스트를 구분하고 미실시를 통과로 기록하지 말라.
- 실제 프롬프트·도구·출처·생성 보완·파일 해시·검증은 감사 기록에 보존하라. 완료 보고에는 원본↔자산 대응, 저장 위치, 핵심 편집과 검증·한계를 간결히 담아라.
- 저장·커밋·푸시·PR·병합·배포는 사용자 승인 범위와 저장소 지침을 따르라. 이 스킬이 게시 권한을 추가하지 않는다. 이미 승인된 작업을 불필요하게 재확인하지 말라.
