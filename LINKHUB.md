# 든든한 장보기 — 링크 모음 페이지 (linkhub)

쇼츠 댓글·설명란의 링크가 클릭되지 않는 유튜브 정책(2023-08-31~) 대응용.
채널 프로필의 클릭 가능한 링크로 연결되는 상품 모음 페이지.

- 공개 URL: https://sundayaa.github.io/jangbogi-links/ (GitHub Pages, 2026-10-02 개설)
- 채널 프로필 링크 문구: 🛒 영상의 상품 보기

## 구조

```
linkhub/
├── products.json      # 상품 데이터 (신규 에피소드마다 맨 앞에 추가)
├── index.html         # 생성 결과물 (직접 편집 금지, build.py가 생성)
├── images/ep02.jpg …  # 상품 대표 이미지
└── bin/build.py       # 생성기 (표준 라이브러리만 사용, 의존성 없음)
```

## 새 상품 추가 절차 (크론용)

1. `products.json`의 `products` 배열 **맨 앞**에 새 상품 객체 추가
   (필드: ep, name, price, price_checked, reviews, rating, image, url, date)
2. 상품 대표 이미지를 `images/epNN.jpg`로 저장
3. `python3 bin/build.py` 실행 → `index.html` 재생성
4. `git add -A && git commit -m "..." && git push` → GitHub Pages 자동 재배포 (1~2분)
5. `updated` 필드를 오늘 날짜로 갱신

## 도구 조사 결론 (2026-10-02)

- **호스팅: GitHub Pages** — 무료·HTTPS·정적 호스팅. 크론에서 git push만으로 재배포.
  기각: Muse 아티팩트 공개 링크 (업데이트마다 사용자 승인 1회 필요 → 하루 3회 자동 갱신과 충돌)
- **Python 라이브러리: 불필요** — 생성기는 json/html/pathlib 표준 라이브러리만으로 충분.
  Jinja2 등 템플릿 엔진은 이 규모에서 이득 없음.
- **JS 라이브러리: 불필요** — 페이지에 JS가 전혀 없음 (구형 폰·느린 네트워크에서도 깨지지 않음).
  "맨 위로" 버튼은 앵커(`#top`)로 구현.
- **GitHub 링크 모음 프로젝트 (littlelink 등) 검토** — SNS 프로필용 작은 버튼 위주라
  상품 카드(큰 이미지·가격·후기수) 레이아웃과 맞지 않아 직접 제작이 더 가벼움.
- **외부 API: 불필요** — 전부 정적 파일.

## 시니어 UX 기준

- 본문 20px, 상품명 27px, 가격 30px, 버튼 24px·높이 76px 이상
- 한 화면 한 상품 카드, 세로 스크롤만
- 파란색 큰 버튼 1개 = "쿠팡에서 상품 보기" (행동이 하나라 헷갈리지 않음)
- 가격 옆에 확인 날짜와 "변동될 수 있어요"를 항상 표기 (미확인 수치 금지 원칙)
- 상·하단 제휴 고지 (쿠팡파트너스)
