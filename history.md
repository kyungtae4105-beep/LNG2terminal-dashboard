# 대화 이력 (History)

> 광양 제2 LNG터미널 증설공사 Dashboard 프로젝트 작업 내역
> 최근 갱신: 2026-05-01
> 작업자: kyungtae@poscointl.com

---

## 세션 개요

POSCO INTERNATIONAL 에너지건설 TF의 **광양 제2 LNG터미널 증설공사 주요 지표 Dashboard** 프로젝트의 사업·제품 문서화 작업.

- 작업 디렉터리: `C:\Users\kyungtae\OneDrive - POSCO INTERNATIONAL\바탕 화면\대시보드`
- Git 브랜치: `main` (작업 시작 시점 clean 상태)
- 최근 커밋:
  - `66394ad` — dashboard.html을 index.html로 이름 변경
  - `f248d69` — 초기 커밋: 광양 LNG터미널 증설공사 대시보드 v1

---

## 대화 1 — BRD.md / PRD.md 생성 요청

### 사용자 요청
> "이 프로젝트의 BRD.md, PRD.md 문서를 각각 생성해줘"

### 수행 작업

#### 1) 프로젝트 구조 파악
- `ls -la` 로 프로젝트 파일 목록 확인
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
- **index.html** — VS Code 스타일 다크 테마, 좌측 Activity Bar + Sidebar + Main 3분할 레이아웃 확인

#### 3) 산출물 생성

**BRD.md (Business Requirements Document)** — 비즈니스 관점
- 사업 배경 및 추진 필요성
- 비즈니스 목표 5개(G1~G5) 및 측정 지표
- 이해관계자 7개 그룹(사업주관·임원·현장PM·데이터입력자·유관부서·발주처·시스템관리자)
- 비즈니스 요구사항 BR-01 ~ BR-12 (우선순위 포함)
- 비기능 요구사항(가용성·성능·보안·유지보수성·확장성·호환성)
- 사업 범위(In/Out of Scope), 가정 및 제약
- 비즈니스 가치 / 기대효과(정량·정성)
- 성공 기준(GO-LIVE / 운영 안정)
- 일정 마일스톤 M1~M4
- 리스크 4개와 대응 방안

**PRD.md (Product Requirements Document)** — 제품 관점
- 페르소나 4명(P1 임원 / P2 현장PM / P3 데이터입력자 / P4 시스템관리자)
- 사용자 시나리오 S1~S5
- 화면(탭) 구성 T1~T7
- 기능 명세 FR-1 ~ FR-8 (BRD의 BR과 추적성 유지)
- 데이터 모델 — `window.DASHBOARD_DATA` TypeScript 스키마, 사진 매니페스트 구조
- 비기능 요구사항 표(성능·보안·호환성·접근성 등)
- 시스템 아키텍처 — 구성도, 기술 스택, 배포 파이프라인
- UX 가이드라인 — 디자인 원칙(VS Code 다크 테마), 인터랙션, 상태 표시
- 운영/유지보수 절차 — 월간 데이터·사진 갱신 SLA, 사용자 관리
- 검증 체크리스트(기능·성능·보안)
- 향후 Backlog BL-01 ~ BL-07
- 변경 이력 표

### 결과
- `BRD.md` (신규 생성)
- `PRD.md` (신규 생성)
- BRD ↔ PRD 간 요구사항 ID 매핑(BR-01~12 ↔ FR-1~8)으로 추적성 확보

---

## 대화 2 — history.md 생성 요청

### 사용자 요청
> "지금까지 우리 대화를 history.md 파일로 정리해줘"

### 수행 작업
- 본 문서(`history.md`) 생성

---

## 현재 프로젝트 문서 구조

```
.
├── README.md          # 프로젝트 소개 (사용자 대상)
├── DEPLOYMENT.md      # 배포·접근제어 가이드 (운영자 대상)
├── BRD.md             # 비즈니스 요구사항 정의서 ← 본 세션에서 생성
├── PRD.md             # 제품 요구사항 정의서 ← 본 세션에서 생성
└── history.md         # 작업 이력 ← 본 세션에서 생성
```

---

## 다음 단계 후보

- 4월 데이터 입력 후 첫 월간 갱신 워크플로우 검증
- BRD/PRD를 사내 결재 양식에 맞춰 변환(필요 시)
- BL-01(자체 도메인), BL-02(PDF 내보내기) 등 Backlog 우선순위 결정

---

## 대화 3 — 2023/2024년 데이터 통합 (2026-05-01)

### 사용자 요청
> "2023년도, 2024년도 파일도 지금 올렸는데 기존에 너가 해준 결과물에다 데이터 추가를 부탁해.
> 이번것도 중요한것은 사진! 사진이 캡션과 잘 부합하는지는 다시한번 검증을해줘.
> 내가 여태껏 추가로 요청 반영했던 사항들 (마일스톤, 세부사항 등) 을 검토하고 반영해줘.
> 시간은 오래걸려도 좋아. 다만, 한가지 첼린지는 이제 데이터 파일이 20개 넘게 추가가 돼서
> 어떻게 분류할지가 중요할거 같은데 너가 검토를 해서 사용자가 쉽게 알아볼 수 있게 작성을 부탁해."

### 신규 PPTX 파일 (22건)
- 2023: 02 / 03 / 04 / 05 / 06(R1) / 07 / 08 / 09 / 10 / 11 / 12월 (11건)
- 2024: 01 / 02 / 03 / 04 / 05 / 06 / 07 / 08 / 09 / 10 / 11월 (11건)

### DRM 보호 파일 (추출 불가)
- 2023-12, 2024-02, 2024-10 — POSCO INTERNATIONAL DRM 적용된 OLE Compound 형식
- 사용자가 PowerPoint에서 열어 일반 PPTX로 다른 이름 저장 시 추출 가능

### 수행 작업

#### 1) 일괄 슬라이드/이미지 추출 (`extract_all_2023_2024.py`)
- 19개 PPTX 추출 (3개 DRM 제외)
- 슬라이드 텍스트 + 이미지 매핑 → `slides_data_legacy.json`

#### 2) KPI 추출 (Agent 분석, `legacy_kpi_extracted.json`)
- 19개월 × #6 탱크(1터미널 마감) + #7,8 탱크(제2 LNG터미널 신축) 각 KPI 분리
- 공정률/계획比, 인원 (관리자/협력사), 안전관리 실적표 (9개 카테고리)
- 발견: 2023-02 시점에 #7,8 탱크 1차계약 진행 중. 2023-08부터 본계약 시작

#### 3) 사진 추출 + 위치 기반 캡션 매칭 (`extract_photos_legacy.py`)
- PPT XML의 좌표(EMU) 기반 정밀 매칭: `<p:pic>` 위치 vs `<p:sp>` 텍스트 박스
- 단일 매칭 + fallback 클러스터링(fragmented PPT 대응)
- 표지/공정률표/안전관리표/Near Miss 페이지 자동 제외
- 결과: 19개월 × 약 13~28장 = 341장 추출

#### 4) 사진 데이터 병합 (`merge_photos.py`)
- 기존 `photos.js` 키 통일: '06월'~'03월' → 'YYYY-MM' 형식
- 사진 폴더 이동: `photos/06월/` → `photos/2025-06/`
- legacy manifest 병합 → 총 29개월 / 733장

#### 5) data.js 통합 (`merge_data.py`)
- 시계열 확장: 2023-02 ~ 2026-03 (38개월, 누락월 포함)
- 메인 진척률(`progress.종합`): 제2 LNG터미널 종합공정률 (2024-01부터, tank78_total 기준)
- 별도 보존:
  - `phase1_progress`: 2023년 #7,8 탱크 단독 진척률 (1차계약/본계약 phase 마커 포함)
  - `tank6_progress`: 1터미널 #6 탱크 마감 진척률 (참고)
- 마일스톤: 기존 69건 + 2023~2024년 16건 추가 (총 85건, 1차계약 → 본계약 전환 마커 포함)
- 안전감사 9개 카테고리 시계열 보강 (legacy 카테고리명 자동 매핑)

#### 6) 분류 체계 (사용자 친화)
- **사이드바 헤더**에 보고기간(2023.02~2026.03, 38개월) + 1차/본계약 표시
- **Overview 상단**에 단계 안내 박스 (계약단계 + 갭월 표시)
- **사진 갤러리**에 연도 필터 추가 (2023/2024/2025/2026 + 전체)
  - 연도 선택 시 해당 연도 월 버튼만 표시 (2단계 drill-down)
  - 월 라벨: `'25.6월` 형식 통일
- **마일스톤 패널**: 기존 분기별 뷰 + 12개 분기 자동 확장
- **localStorage 키 버전 업** (v2→v3, photos v1→v2): 옛 키 형식과 충돌 방지

### 데이터 갭
- DRM 추출 불가: 2023-12, 2024-02, 2024-10
- 보고서 미보유: 2024-12, 2025-01 ~ 2025-05
- `data.project.data_gap_reason`에 사유 명시

### 결과 파일
- `data.js`: 38개월 통합 시계열, 마일스톤 85건
- `photos.js`: 29개월 / 733장 / YYYY-MM 키 통일
- `photos/`: 폴더 구조 통일 (`2023-02/` ~ `2026-03/`)
- 보조: `legacy_kpi_extracted.json`, `slides_data_legacy.json`, `photos_manifest_legacy.json`

---

© 2026 POSCO INTERNATIONAL — 에너지건설 TF
