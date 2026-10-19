# 사진별 정리·보존 규칙

| 대상 | 정리할 요소 | 보존할 요소 |
|---|---|---|
| 차창·창문 촬영 | 유리에 겹친 실내 조명, 좌석·휴대폰·촬영자 반사, 렌즈 플레어 | 실제 창틀·건물 유리, 외부 풍경, 자연광과 그림자 |
| 건축·유적 | 전봇대·전선, 우발적 사람·모자·팔·손·하단 군중 | 아치·돔·첨탑 개수, 창 위치, 벽돌과 문양, 조각·부조의 인물 |
| 풍경·호수 | 차창 반사, 우발적 관광객, 전선 | 산 능선, 지평선, 실제 연못·호수의 반영과 물결 |
| 인물·기념사진 | 주인공 주변 행인과 가림 요소 | 주인공의 얼굴·체형·복장·자세·손, 동행인으로 지정된 사람 |
| 음식·실내 | 가장자리 우발적 손가락·불필요한 반사 | 음식·식기 형태, 의도된 실내 물건, 메뉴의 사실 정보 |
| 박물관·문헌 | 관람객 팔·손, 진열 유리의 우발적 반사 | 유물·문자, 수치·지도·표의 의미 |

## 판단 기준

- 반사 제거는 촬영을 방해한 **유리 반사**에 적용하라. 모히 호사의 연못 반영이나 이식쿨의 수면은 지우지 말라.
- 건물·풍경 사진은 하단 단체관광객을 정리하라. 인물 사진에 이를 일괄 적용하여 주인공을 삭제하지 말라. 주인공 선택이 불명확하고 결과를 크게 바꾸면 대상만 짧게 확인하라.
- 티무르 기마상·울루그벡 동상과 그 손은 군중이 아니다. 벽화 사절·새·사슴·태양·암각화도 보존하라. 원본에서 안 보이는 문양·문자를 발명하지 말라.
- 아프라시압 벽화의 실제 보이는 깃털 관모를 선명하게 하되 역사 해석을 이미지로 확정하지 말라. 유골함 회전 요청은 내용물의 위아래를 원본과 대조하라.
- 유리 덮개·펜스·난간은 자동 삭제 대상이 아니다. 요청이 있고 핵심 피사체를 보존할 때만 제거하라. 주변 구조물을 새로운 역사적 건물로 채우지 말라.
- 상단 보완은 최소 범위로 생성하라. 건물 외곽과 작은 하늘 여백이 보이는지 확인하고 원본에 없던 세부는 감사 기록에 생성 보완으로 표시하라. 이를 실측 복원 자료로 쓰지 말라.
- 수채화는 투명하고 절제된 색면·가벼운 종이 질감, 색연필화는 정교한 선과 자연스러운 질감으로 통일하라. 과포화·과장·가짜 글자를 피하라.

## 프롬프트 골격

실제 사진에 해당하는 항목만 채워라. 모든 사진에 삭제 목록을 기계적으로 붙이지 말라.

```text
Use case: style-transfer with precise-object-edit.
Asset: one illustration for the existing Korean travel guide.
Input 1: edit target [filename and identified subject].
Input 2, if supplied: style reference only [filename].
Keep: [portrait identity / exact architecture / specific motifs / perspective / natural water reflections].
Remove only: [observed window glare / poles and wires / incidental foreground crowds / intrusive fingers].
Framing: [preserve source ratio and crop; OR explicitly requested minimal top outpainting and sky margin].
Style: restrained transparent watercolor washes with fine colored-pencil details; match the reference.
Constraints: preserve the designated portrait subject and historical sculptures; no invented readable inscriptions, ornaments, people, extra buildings, captions, watermark or border.
```

## 출처와 표시

- 외부 원본 페이지를 확인하고 저작자·날짜·라이선스 URL·고정판·확인일·허용 범위와 실제 수정 내용을 기록하라. “Commons에 있음”만으로 검토를 끝내지 말라.
- CC BY는 크레딧·원본/라이선스 링크·수정 표시를, CC BY-SA는 해당 배포 조건까지 준수하라. 현재 조건은 원본에서 확인하라. CC0도 추적용 출처 기록을 남겨라.
- 미확인 인터넷 캡처를 AI로 변환해 공개하지 말라. 확인이 안 되면 허용된 대체 사진으로 새로 제작하고 두 자료의 기록을 혼합하지 말라.
- 일반 한글 캡션은 장소와 가시적 특징으로 작성하라. “사진을 바탕으로 그린”, “사용자 제공”, “AI 생성”, “재해석”을 넣지 말라. **필수 저작자·라이선스·수정 표시는 생략하지 말고** 별도 크레딧/출처 영역에 표시하라. 감사 문서만으로 이용자에게 필요한 표시 의무를 충족한다고 추정하지 말라.
