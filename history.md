# 대화 이력 (History)

> 광양 제2 LNG터미널 증설공사 Dashboard 프로젝트 작업 내역
> 작성일: 2026-04-30
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

© 2026 POSCO INTERNATIONAL — 에너지건설 TF
