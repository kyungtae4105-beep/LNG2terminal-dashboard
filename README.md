# 광양 제2 LNG터미널 증설공사 — 주요 지표 Dashboard

POSCO INTERNATIONAL 에너지건설 TF의 주요 지표(공정/안전/인력/현장사진)를 통합 시각화하는 정적 웹 대시보드.

## 🔐 접근 권한

이 대시보드는 **승인된 사용자만 접근**할 수 있습니다.

**접근 요청**: 대시보드 사용을 원하는 분은 `kyungtae@poscointl.com` 으로 메일을 보내주세요. 검토 후 화이트리스트에 추가됩니다. 등록된 이메일 주소로 OTP 코드가 발송되어 로그인할 수 있습니다.

## 📋 주요 기능

- **종합 대시보드**: 게이지·S-curve·KPI·인력·안전·교육 통합 뷰
- **공정 관리**: 공구별(육상부/해상부/154kV) 월별 공정률 + 편차 분석
- **시공/자원관리**: 인력 stacked bar + 관리자/협력 비율
- **안전 관리**: 무재해 일수 / Near Miss / 교육 / 지적 분류
- **월별 작업사진**: 1·2·3월 PPT 추출 사진 112장 + 캡션 (필터·라이트박스)
- **마일스톤**: 1Q 실적 / 차월 계획
- **데이터 편집**: 모든 지표 인라인 수정 + JSON 내보내기/불러오기

## 🛠 기술 스택

- 정적 HTML / CSS / JavaScript
- [Chart.js v4](https://www.chartjs.org/) (CDN)
- 빌드 도구 없음 — 더블클릭으로 즉시 실행 가능

## 📁 파일 구조

```
.
├── index.html            # 메인 대시보드 페이지 (Cloudflare Pages 진입점)
├── data.js               # 프로젝트 지표 데이터 (편집 가능)
├── photos.js             # 사진 매니페스트 (PPT 추출 결과)
├── photos/               # 작업 사진 112장 (월별)
│   ├── 01월/
│   ├── 02월/
│   └── 03월/
├── slides_data.json      # PPT 슬라이드 raw 추출 결과
├── photos_manifest.json  # 사진 매니페스트 raw
├── extract_slides.py     # PPT → 슬라이드 데이터 추출 스크립트
├── build_photo_manifest.py  # 사진 매니페스트 빌드 스크립트
└── README.md
```

> 원본 PPT 파일과 `ppt_extract/` 임시 폴더는 `.gitignore`로 제외됩니다. 사진을 다시 빌드해야 할 때만 PPT 파일을 로컬에 두고 두 스크립트를 다시 실행하면 됩니다.

## 🚀 배포

- **호스팅**: Cloudflare Pages (자동 배포 — `main` 브랜치 push 시)
- **접근 제어**: Cloudflare Access (이메일 OTP + 화이트리스트)

자세한 배포·접근 제어 설정은 [`DEPLOYMENT.md`](./DEPLOYMENT.md) 참고.

## 📝 데이터 갱신

월간 데이터를 갱신할 때:

1. 대시보드의 **데이터 편집** 탭에서 직접 수정 → **JSON 내보내기**
2. 다운로드한 JSON으로 `data.js` 의 `window.DASHBOARD_DATA` 값을 교체
3. git commit & push → Cloudflare Pages가 자동으로 재배포

월별 사진을 추가할 때:

1. 새 PPT 파일을 로컬에 두고
2. `python extract_slides.py` 와 `python build_photo_manifest.py` 실행
3. `photos/` 폴더와 `photos.js` 가 갱신됨
4. git commit & push

---

© 2026 POSCO INTERNATIONAL — 에너지건설 TF
