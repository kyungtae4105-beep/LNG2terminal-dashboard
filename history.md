# 대화 이력 (History)

> 광양 제2 LNG터미널 증설공사 Dashboard 프로젝트 작업 내역
> 최근 갱신: 2026-05-06
> 작업자: kyungtae@poscointl.com

---

## 세션 개요

POSCO INTERNATIONAL 에너지건설 TF의 **광양 제2 LNG터미널 증설공사 주요 지표 Dashboard** 프로젝트의 사업·제품 문서화 + 디자인 정비 작업.

- 작업 디렉터리: `C:\Users\kyungtae\OneDrive - POSCO INTERNATIONAL\바탕 화면\대시보드`
- Git 원격: `https://github.com/kyungtae4105-beep/LNG2terminal-dashboard` (Private)
- 호스팅: Cloudflare Pages (자동 배포 — `main` push)
- 접근 제어: Cloudflare Access (Email OTP + 화이트리스트)

---

## 대화 1 — BRD.md / PRD.md 생성 요청 (2026-04)

### 사용자 요청
> "이 프로젝트의 BRD.md, PRD.md 문서를 각각 생성해줘"

### 수행 작업

#### 1) 프로젝트 구조 파악
- 핵심 파일: `index.html`, `data.js`, `photos.js`, `photos_manifest.json`
- 데이터 추출 스크립트: `extract_slides.py`, `build_photo_manifest.py`
- 문서: `README.md`, `DEPLOYMENT.md`
- 원본 자료: 과제정의서 PPT, 1·2·3월 건설실적 PPT, `slides_data.json`, `slides_summary.txt`
- 디렉터리: `photos/`, `ppt_extract/`, `.git/`

#### 2) 핵심 문서 검토
- **README.md** — 프로젝트 개요·기능·기술스택·파일구조·배포 방식 파악
- **DEPLOYMENT.md** — Cloudflare Pages + Cloudflare Access(이메일 OTP + 화이트리스트) 배포 절차 파악
- **data.js** — 데이터 스키마 분석:
  - `project`, `progress`, `manpower`, `no_accident_days`
  - `safety_audit_land` (지적사항 9분류)
  - `safety_edu_land` (교육 4종)
  - `incident_summary`, `milestones`, `next_month_plan`
  - 공구 구성: 종합 / 육상부 / 해상부 / 154kV
- **index.html** — VS Code 스타일 라이트 테마, 좌측 Activity Bar + Sidebar + Main 3분할 레이아웃 확인

#### 3) 산출물 생성
- **BRD.md** — 사업 배경·목표·이해관계자·BR-01~12·NFR·In/Out Scope·리스크
- **PRD.md** — 페르소나·시나리오·탭 구성·FR 명세·데이터 모델·아키텍처·UX·운영
- BRD ↔ PRD 간 요구사항 ID 매핑(BR ↔ FR)으로 추적성 확보

---

## 대화 2 — 38개월 데이터 통합 (2026-04~05)

### 작업 내용
- 2023.02~2024.11 legacy PPT 데이터 추출(`extract_legacy.py`, `extract_all_2023_2024.py`)
- `legacy_kpi_extracted.json` → `data.js` 머지(`merge_data.py`)
- 사진 매니페스트 통합(`merge_photos.py`)
- 누락월 9개(2023-12, 2024-02·10·12, 2025-01~05) `data_gaps` 메타로 명시
- 38개월 시계열 + 사진 341장 적재
- 안전관리 차트 3종(무재해 일수, 지적, 교육)을 2026-01부터 표시하도록 슬라이스
- 종합 추세선 빨강 굵기 강조

### 커밋 (관련)
- `0c323c0` — 2023.02~2024.11 데이터 통합: 38개월 시계열 + 사진 341장 추가
- `7ea8792` — 종합대시보드/공정·시공·안전 탭 최근 10개월 표시 + 종합 추세선 빨강 굵기 강조
- `6132c21` — 프로젝트 정보 담당자 표기 수정 + AS-IS/TO-BE SAP·RPA 항목 정리, 사진 기본 연도 '전체', 154kV 무재해 '완료', 공구별 S-curve 종합 라인 빨강 강조
- `ab321e5` — 안전관리 차트 3종 2026-01부터 표시

---

## 대화 3 — 개발자용 설계서 작성 (2026-05-06)

### 사용자 요청
> "나는 앱 설계전문가입니다. 개발자가 이 폴더의 내용을 구체적으로 확인할수 있도록 설계서를 작성해야 합니다. 설계서는 Readme.md 파일로 만들어줘"

### 수행 작업

#### 1) 폴더 전수 조사
- `index.html` (3,488 LOC) 코드 맵 작성 — 50여 개 핵심 함수 라인 번호 인덱싱
- `data.js` (2,305 LOC) 스키마 분석 — 8개 최상위 섹션 식별
- `photos.js` (3,784 LOC) 매니페스트 구조 파악
- `photos/` 39개 월별 폴더 / 341장 사진 카운트
- Python 추출 스크립트 7종 책임 분리 정리
- `_headers` 캐시·보안 정책 검토

#### 2) README.md 전면 재작성 (개발자용 설계서)
기존 README는 사용자/관리자 개요였으나, **개발자가 코드를 곧바로 만질 수 있는 구체성**으로 재구성:
- 폴더/파일 구조 (모든 산출물의 책임)
- 시스템 아키텍처 다이어그램 + Cloudflare 흐름 + `_headers` 정책
- 데이터 모델 — TypeScript 스키마, 무결성 규칙 D-1~D-6, 누락월 9개 사유
- 사진 매니페스트 스키마 + 폴더 명명 규칙
- UI 구조 — 9개 탭, 컬러 팔레트, 공구별 차트 색상 관행
- `index.html` 코드 맵 — 핵심 함수 라인 번호 인덱스, `PANELS`/`PANEL_INIT` 컨벤션, 데이터 흐름
- Python 추출 파이프라인 — 7개 스크립트 입출력/책임, `merge_data.py:17` 하드코딩 경로 함정
- 신규 월/공구/KPI 추가 가이드 + Chart.js 추가 패턴 스니펫
- 트러블슈팅 — OneDrive 동기화 충돌, CDN 차단 등

---

## 대화 4 — 디자인 재정비 명세 + 4종 문서 갱신 (2026-05-06)

### 사용자 요청
1. (1차) 디자인 명세 제공 — 7개 탭(Activity Bar 아이콘 📊·📈·👷·🛡️·📷·✏️·ℹ️), 4개 핵심 탭(Overview/Progress/Photos/Editor) 상세, 컬러 팔레트(육상부 `#2563eb` / 해상부 `#0891b2` / 154kV `#ea580c` / 종합 `#dc2626`), Single File 구조 유지
2. (2차) 문서 4종 갱신 요청 — BRD.md / PRD.md / DEPLOYMENT.md / history.md

### 수행 작업

#### 1) BRD.md v1.1
- 보고기간을 **2023-02~2026-03 (38개월)** 로 갱신
- BR-13 추가 — 누락월 사유 명시 + 차트 단절 방지
- 사업 가치(`G6 운영 비용 최소화`) 추가
- 일정 마일스톤에 M3(38개월 적재)·M5(재설계) 추가
- 리스크에 PPT DRM / CDN 차단 항목 추가
- 변경 이력 v1.1 기록

#### 2) PRD.md v1.1
- 탭 구성을 7개로 명문화 (overview / progress / resource / safety / photos / editor / info)
- 컬러 팔레트를 명세에 맞춰 통일 (육상 `#2563eb`, 해상 `#0891b2`, 154kV `#ea580c`, 종합 `#dc2626`)
- FR-2.4(누락월 자동 갭 처리), FR-6.5(localStorage 임시 저장), FR-7(프로젝트 정보 탭) 추가
- 시나리오 S6(38개월 추세 분석) 추가
- BL-08(Chart.js / Pretendard self-host) 백로그 추가
- 데이터 모델 섹션에 `phase1_progress` / `tank6_progress` legacy 보존 명시

#### 3) DEPLOYMENT.md v1.1
- 실제 GitHub 저장소 URL(`kyungtae4105-beep/LNG2terminal-dashboard`) 명시
- 0단계 한눈에 보기 다이어그램 추가
- `_headers` 정책 검증 절차 추가
- 4-4 롤백 절차(Cloudflare Pages Deployments 탭) 추가
- 트러블슈팅에 사내망 CDN 차단 / `_headers` 위치 / 누락월 차트 / 사진 권한 항목 추가
- `.gitignore` 권장 항목 명시

#### 4) history.md (본 문서)
- 대화 1 ~ 4 정리
- 관련 커밋 해시 / 날짜 / 영향 범위 기록

---

## 주요 산출물 인벤토리 (현재 시점 — 2026-05-06)

| 파일 | 역할 | 상태 |
|---|---|---|
| `index.html` | 메인 페이지 (UI + JS, ~3,488 LOC) | 운영 중 |
| `data.js` | 지표 데이터 (38개월) | 운영 중 |
| `photos.js` | 사진 매니페스트 (341장) | 운영 중 |
| `_headers` | Cloudflare 캐시·보안 헤더 | 운영 중 |
| `assets/posco_intl_logo.png` | 타이틀바 로고 | 운영 중 |
| `photos/` (39 폴더) | 작업 사진 | 운영 중 |
| `README.md` | 개발자용 설계서 | v1.1 (2026-05-06) |
| `BRD.md` | 비즈니스 요구사항 | v1.1 (2026-05-06) |
| `PRD.md` | 제품 요구사항 | v1.1 (2026-05-06) |
| `DEPLOYMENT.md` | 배포·접근제어 가이드 | v1.1 (2026-05-06) |
| `history.md` | 작업 이력 (본 문서) | v1.1 (2026-05-06) |
| `extract_*.py` / `merge_*.py` / `build_photo_manifest.py` | 데이터 추출 파이프라인 | 사진 갱신 시 사용 |

---

## 이후 진행 예정 (2026-05~)

- [ ] 명세에 맞춘 `index.html` 디자인 재정비 (컬러 팔레트 통일, KPI 카드 4종 정렬)
- [ ] 4월 데이터 입력 후 첫 정기 갱신 사이클 검증
- [ ] 사용자 화이트리스트 정식 운영
- [ ] BL-08 Chart.js / Pretendard self-host 옵션 검토 (사내망 CDN 정책 확인 시)

---

© 2026 POSCO INTERNATIONAL — 에너지건설 TF
연락 / 접근 신청: **kyungtae@poscointl.com**
