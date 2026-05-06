# 광양 제2 LNG터미널 증설공사 — 주요 지표 Dashboard 설계서

> **프로젝트**: POSCO INTERNATIONAL 에너지건설 TF · 주요 지표 Dashboard
> **문서 종류**: 개발자용 설계서 (Software Design Document)
> **버전**: v1.1 (2026-05)
> **관련 문서**: [BRD.md](./BRD.md) · [PRD.md](./PRD.md) · [DEPLOYMENT.md](./DEPLOYMENT.md) · [history.md](./history.md)

이 문서는 본 폴더(`대시보드/`)의 모든 산출물을 **개발자가 즉시 코드에 손을 댈 수 있을 정도**로 구체적으로 풀어낸 설계서입니다. 비즈니스/제품 요구사항은 BRD/PRD를 참고하고, 본 설계서는 **구현·구조·데이터·운영 절차**에 집중합니다.

---

## 목차

1. [프로젝트 한눈에 보기](#1-프로젝트-한눈에-보기)
2. [기술 스택 & 설계 원칙](#2-기술-스택--설계-원칙)
3. [폴더 / 파일 구조](#3-폴더--파일-구조)
4. [시스템 아키텍처](#4-시스템-아키텍처)
5. [데이터 모델 (`data.js`)](#5-데이터-모델-datajs)
6. [사진 매니페스트 (`photos.js`)](#6-사진-매니페스트-photosjs)
7. [UI 구조 — 탭 / 컴포넌트](#7-ui-구조--탭--컴포넌트)
8. [`index.html` 코드 맵](#8-indexhtml-코드-맵)
9. [데이터 추출 파이프라인 (Python)](#9-데이터-추출-파이프라인-python)
10. [상태 저장 & 영속화](#10-상태-저장--영속화)
11. [빌드 / 배포](#11-빌드--배포)
12. [개발 환경 설정](#12-개발-환경-설정)
13. [확장 가이드](#13-확장-가이드)
14. [트러블슈팅](#14-트러블슈팅)
15. [부록 — 용어 / 명명 규칙](#15-부록--용어--명명-규칙)

---

## 1. 프로젝트 한눈에 보기

| 항목 | 내용 |
|---|---|
| 제품명 | 광양 제2 LNG터미널 증설공사 주요 지표 Dashboard (`lng-dashboard`) |
| 형태 | 정적 단일 페이지(SPA-Like) HTML — `index.html` 더블클릭으로도 동작 |
| 데이터 | `data.js` (JS 전역 객체) + `photos.js` (PPT 추출 사진 매니페스트) |
| 차트 | Chart.js v4 (CDN) |
| 호스팅 | Cloudflare Pages (자동 배포 — `main` push) |
| 접근 제어 | Cloudflare Access (이메일 OTP + 화이트리스트) |
| 보고기간 | **2023-02 ~ 2026-03** (38개월, 일부 갭 9개월 포함) |
| 공구 분할 | 종합 / 육상부 / 해상부 / 154kV |
| 작업 사진 | 39개 월별 폴더, 총 341장 + 캡션 |

### 핵심 가치
- **빌드리스(Buildless)** — Node/Webpack 없음. CDN의 Chart.js 외 외부 의존 0
- **편집 가능 데이터** — 브라우저 UI 인라인 편집 → JSON 내보내기 → `data.js` 교체 → `git push`
- **사진까지 통합** — 분기별 PPT의 작업사진을 월/공종 필터 + 라이트박스로 열람

---

## 2. 기술 스택 & 설계 원칙

### 2.1 기술 스택
| 레이어 | 기술 | 비고 |
|---|---|---|
| 마크업 | HTML5 | 단일 `index.html` (3,488 LOC) |
| 스타일 | 임베디드 CSS3 (`<style>`) | CSS Variables 기반 라이트 테마 |
| 스크립트 | ES6 JavaScript (No framework) | 모든 코드가 `index.html` 하단 단일 `<script>` 블록 |
| 차트 | Chart.js v4.4.1 (CDN) | UMD 빌드 |
| 폰트 | Pretendard + Inter (CDN) | Google Fonts + jsDelivr |
| 데이터 | `window.DASHBOARD_DATA`, `window.PHOTOS_DATA` | 전역 객체 |
| 빌드 도구 | **없음** | `package.json`도 없음 |
| 영속화 | `localStorage` (편집 임시 저장) + `git` (정식 반영) |
| 추출 도구 | Python 3 — `python-pptx` 등 | 사진/슬라이드 갱신 시에만 사용 |

### 2.2 설계 원칙
1. **No Build Step** — 운영 인력이 빌드/CI를 학습할 필요 없도록 정적 자산만 배포
2. **Data-as-Code** — 데이터는 `data.js`의 JS 객체. 편집 도구는 동일 페이지 안에서 내장
3. **Single File UI** — 라우팅/번들링 복잡도를 피하기 위해 모든 UI를 `index.html` 하나에 둠
4. **Fail-Soft on Missing Data** — `null` 값은 차트에서 자동 갭 처리, 카드에서는 `—` 표시
5. **공구 식별자는 한글 그대로** — `육상부`, `해상부`, `154kV`, `종합` 키 사용 (원본 보고서 호환)

---

## 3. 폴더 / 파일 구조

```
대시보드/
├── index.html                    # 메인 페이지 (UI + 모든 JS, ~3,488 LOC)
├── data.js                       # 지표 데이터 (window.DASHBOARD_DATA, ~2,305 LOC)
├── photos.js                     # 사진 매니페스트 (window.PHOTOS_DATA, ~3,784 LOC)
├── _headers                      # Cloudflare Pages 캐시/보안 헤더
│
├── README.md                     # ← 본 설계서
├── BRD.md                        # 비즈니스 요구사항
├── PRD.md                        # 제품 요구사항
├── DEPLOYMENT.md                 # 배포·접근제어 가이드
├── history.md                    # 작업 이력
│
├── assets/
│   └── posco_intl_logo.png       # 타이틀바 로고
│
├── photos/                       # 작업 사진 (341장)
│   ├── 01월/  02월/  03월/        # 2026년 1Q (단축 표기)
│   ├── 06월/ ... 12월/            # 2025년 후반(단축 표기)
│   ├── 2023-02/ ... 2024-11/     # 2023~2024 (전체 표기)
│   └── 2025-06/ ... 2026-03/     # 2025~2026 (전체 표기)
│
├── ppt_extract/                  # PPT 압축 해제 임시 폴더 (.gitignore 예정)
│
├── slides_data.json              # PPT 슬라이드 raw 추출 결과 (1Q)
├── slides_data_legacy.json       # 2023~2024 PPT raw 추출 결과
├── slides_summary.txt            # 추출 요약 (사람 확인용)
├── photos_manifest.json          # 사진 매니페스트 raw (1Q)
├── photos_manifest_legacy.json   # 2023~2024 매니페스트 raw
├── legacy_kpi_extracted.json     # 2023~2024 KPI 추출 결과
│
├── extract_slides.py             # PPT XML → slides_data.json
├── extract_legacy.py             # 2023~2024 PPT 일괄 추출
├── extract_all_2023_2024.py      # 2023~2024 KPI 한꺼번에 추출
├── extract_photos_legacy.py      # 2023~2024 사진 추출
├── build_photo_manifest.py       # 사진 manifest → photos.js 빌드
├── merge_data.py                 # legacy KPI를 data.js에 머지
└── merge_photos.py               # 사진 매니페스트 머지
```

> `[에너지건설TF] 주요 지표 Dashboard 과제정의서 (260311).pptx` 가 작업 디렉터리에 있을 수 있으나 운영 산출물은 아니며 git 추적 대상 외입니다.

### 폴더 명명 혼합 규칙
- `01월 / 02월 / 03월` 폴더는 **2026년 1Q** (PRD 작성 시점의 “현재 분기” 단축 표기)
- `YYYY-MM` 형태 폴더는 그 외 모든 월
- 신규 월을 추가할 때는 **`YYYY-MM` 형태로 통일**할 것 (단축 표기는 1Q 호환을 위해서만 유지)

---

## 4. 시스템 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                    사용자 브라우저 (Chrome/Edge/Safari)         │
│                                                                │
│   ┌──────────────────────────────────────────────────────┐   │
│   │ index.html (단일 페이지)                              │   │
│   │   ├─ <head>  : Pretendard + Chart.js v4 (CDN)        │   │
│   │   ├─ <body>  : Activity Bar / Sidebar / Tabs / Panels │   │
│   │   └─ <script>: 9개 PANELS, 차트 렌더, 편집 로직      │   │
│   └──────────────────────────────────────────────────────┘   │
│           ▲ data.js (전역 DASHBOARD_DATA)                     │
│           ▲ photos.js (전역 PHOTOS_DATA)                      │
│           ▲ photos/**/* (정적 이미지)                          │
│           ▲ assets/posco_intl_logo.png                        │
└──────────────────────────────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Cloudflare Access (Email OTP + 화이트리스트)                  │
└──────────────────────────────────────────────────────────────┘
                       │ 인증 통과
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Cloudflare Pages   ◀── git push (main) ── GitHub Private Repo│
│  (정적 서빙, build cmd 없음)                                  │
│  └─ _headers (캐시·보안 헤더)                                 │
└──────────────────────────────────────────────────────────────┘

[관리자 로컬]
   ┌──────────────────────────────────────────────┐
   │ 월간 PPT (DRM 해제본) ─► extract_slides.py    │
   │                          ─► build_photo_manifest.py │
   │                          ─► merge_*.py         │
   │   → data.js / photos.js / photos/ 갱신       │
   └──────────────────────────────────────────────┘
```

### `_headers` 정책 요약
- `/photos/*` → `Cache-Control: public, max-age=31536000, immutable` (사진은 변경 안 함)
- `/*.js` → `max-age=300` (5분, 데이터 갱신 빠르게 반영)
- `/*.html` → `max-age=60` + `X-Frame-Options: DENY` + `nosniff` + `Referrer-Policy: same-origin`

---

## 5. 데이터 모델 (`data.js`)

`data.js` 는 단 한 줄의 전역 할당으로 시작합니다:
```js
window.DASHBOARD_DATA = { /* ... */ };
```

### 5.1 최상위 스키마

```ts
{
  project: {
    name: string,           // "광양 제2 LNG터미널 증설공사"
    owner: string,          // "에너지건설 TF"
    report_period: string,  // "2023년 2월 ~ 2026년 3월"
    purpose: string,
    phases: { name, start, end, desc }[],   // "1차 계약" / "본 계약"
    data_gaps: string[],                    // 누락월 9개 ("YYYY-MM")
    data_gap_reason: { [month]: string }    // 누락 사유
  },

  progress: {
    months: string[],   // 38개 ("2023-02" ~ "2026-03")
    종합:   { plan: (number|null)[], actual: (number|null)[] },
    육상부: { plan: ..., actual: ... },
    해상부: { plan: ..., actual: ... },
    "154kV": { plan: ..., actual: ... }
  },

  manpower: {
    months: string[],
    종합 / 육상부 / 해상부 / 154kV: {
      manager: (number|null)[],   // 관리자(원청)
      partner: (number|null)[]    // 협력사
    }
  },

  no_accident_days: {
    months: string[],
    육상부 / 해상부 / 154kV: (number|null)[]
  },

  safety_audit_land: {
    months: string[],
    추락 / 전도 / "낙하·비래" / 감전 / "충돌·협착" /
    "붕괴·도괴" / "화재·폭발" / 질식 / 기타 : number[]
  },

  safety_edu_land: {
    months: string[],
    "채용·작업변경" / 특별교육 / 관리감독자 / 정기교육 : number[]
  },

  incident_summary: [
    { sub: "육상부"|"해상부"|"154kV",
      공상: number, 일반재해: number, 중대재해: number,
      일반NearMiss: number, 중대NearMiss: number }
  ],

  phase1_progress: {       // 1차계약 (2023-02~2023-07) + 본계약 초기
    months: string[],
    phase: ("1차계약"|"본계약")[],
    tank78_actual: number[],
    tank78_plan_ratio: number[]
  },

  tank6_progress: {        // #6 탱크 (참고용 legacy)
    months: string[],
    "진척률": number[]
  },

  milestones: [
    { date: "YYYY-MM-DD",
      sub: "육상-토목"|"육상-기계"|"육상-전기"|"해상-..."|"154kV",
      공종: "토목"|"기계"|"전기"|"건축"|"부두공"|"기타",
      title: string,
      status: "착수"|"진행"|"완료" }
  ],

  next_month_plan: [
    { date: "YYYY-MM-DD", 공종: string, title: string }
  ]
}
```

### 5.2 데이터 무결성 규칙
| # | 규칙 | 위반 시 결과 |
|---|---|---|
| D-1 | 각 섹션의 `months[]` 길이 = 해당 섹션의 모든 시계열 배열 길이 | 차트 인덱스 미스매치 |
| D-2 | 누락월은 `null` 로 채움 (`undefined` 금지) | Chart.js가 제대로 갭 처리하지 못함 |
| D-3 | `data_gaps`와 실제 `null` 위치 일치 | 사용자 안내 vs 표시 불일치 |
| D-4 | `incident_summary` 의 `sub` 는 `육상부 / 해상부 / 154kV` 셋 중 하나 | 안전 카드 렌더 누락 |
| D-5 | `milestones[].date` ISO 형식 (`YYYY-MM-DD`) | 정렬 불가 |
| D-6 | 공구 키는 한글 표기 고정 (`종합 / 육상부 / 해상부 / 154kV`) | 코드 곳곳의 lookup 실패 |

### 5.3 누락월 (현재 9개월)
| 월 | 사유 |
|---|---|
| 2023-12 | 보고서 DRM 보호로 추출 불가 |
| 2024-02 | 보고서 DRM 보호로 추출 불가 |
| 2024-10 | 보고서 DRM 보호로 추출 불가 |
| 2024-12 | 보고서 미보유 |
| 2025-01 ~ 2025-05 | 보고서 미보유 |

---

## 6. 사진 매니페스트 (`photos.js`)

```js
window.PHOTOS_DATA = {
  "YYYY-MM": [           // 또는 "01월"/"02월"/"03월" (1Q 단축표기)
    {
      title: string,                         // 슬라이드 타이틀
      category: "육상부"|"해상부"|"154kV",     // 공구
      type: "공정사진"|"안전점검"|"공사사진"|...,
      items: [
        { file: "photos/.../xxx.jpeg",
          caption: string }                  // 캡션 (날짜 포함 권장)
      ],
      slide: number                          // 원본 PPT 슬라이드 번호
    },
    ...
  ],
  ...
}
```

- **키 정책**: 1Q는 `01월/02월/03월`, 그 외는 `YYYY-MM` 사용 (폴더명과 1:1)
- **경로**: `items[].file` 은 항상 `photos/<key>/<filename>` 으로 시작
- **수정 정책**: 직접 편집은 권장하지 않음. PPT → 추출 스크립트 → 자동 생성 흐름을 유지하고, 캡션 보정만 인라인 편집(데이터 편집 탭)으로 처리

---

## 7. UI 구조 — 탭 / 컴포넌트

### 7.1 레이아웃 (VS Code 스타일)
```
┌─ Title bar (52px) ────────────────────────────────────────┐
│ [POSCO INTL Logo] | 광양 제2 LNG터미널 ...     [- □ ×]    │
├─Activity─┬─Sidebar (260px)───────┬─Editor──────────────────┤
│   📊     │ 📋 종합               │ ┌Tabs──────────────────┐│
│   📈     │   📊 종합 대시보드     │ │ 📊 종합  📈 공정 ... ││
│   👷     │ 🏗️ 프로젝트            │ ├Panels────────────────┤│
│   🛡️     │   📈 공정 관리         │ │ <차트, 표, 편집기 등>││
│   📷     │   👷 시공/자원관리     │ │                      ││
│   🎯     │   🛡️ 안전 관리          │ │                      ││
│   ✏️     │ 📷 현장 기록           │ │                      ││
│   ℹ️     │   📷 월별 작업사진     │ │                      ││
│          │   📤 사진 업로드/관리  │ │                      ││
│          │   🎯 마일스톤          │ │                      ││
│          │ ⚙️ 관리                │ │                      ││
│          │   ✏️ 데이터 편집       │ │                      ││
│          │   ℹ️ 프로젝트 정보     │ └──────────────────────┘│
├──────────┴───────────────────────┴─────────────────────────┤
│ 📍광양 | 👤TF | 📅2023-02~2026-03(38M) ... | UTF-8 | Ready │
└────────────────────────────────────────────────────────────┘
```

### 7.2 탭 정의 (`TAB_DEFS` — `index.html:927`)

| key | 타이틀 | 아이콘 | 핵심 컴포넌트 |
|---|---|---|---|
| `overview` | 종합 대시보드 | 📊 | 진행률 게이지, S-curve, KPI 카드, 인력/안전/교육 요약 |
| `progress` | 공정 관리 | 📈 | 공구별 월별 공정률 라인차트, 계획/실적 편차표 |
| `resource` | 시공/자원관리 | 👷 | 인력 stacked bar (관리자/협력) + 비율 표 |
| `safety` | 안전 관리 | 🛡️ | 무재해 일수 카드, Near Miss/재해 표, 지적사항 9분류, 교육 4종 |
| `photos` | 월별 작업사진 | 📷 | 월/공종 필터 + 썸네일 그리드 + 라이트박스 |
| `upload` | 사진 업로드/관리 | 📤 | 드래그&드롭 업로드 큐, 캡션 편집 |
| `milestones` | 마일스톤 | 🎯 | 1Q 실적표 + 차월 계획표 |
| `editor` | 데이터 편집 | ✏️ | 전 지표 인라인 편집 + JSON 내보내기/불러오기 |
| `info` | 프로젝트 정보 | ℹ️ | AS-IS / TO-BE / 구성요소 설명 |

### 7.3 컬러 팔레트 (CSS Variables — `index.html:14`)
```css
--bg: #f8fafc;       --surface: #ffffff;
--text: #0f172a;     --text-muted: #64748b;
--primary: #2563eb;  --primary-soft: #dbeafe;
--success: #15803d;  --danger: #b91c1c;  --warning: #c2410c;
```
- **공구별 차트 색상 관행**: 육상부=청색, 해상부=청록, 154kV=주황, 종합=빨강(굵게)

---

## 8. `index.html` 코드 맵

`index.html` 의 `<script>` 블록은 약 2,500 LOC로 가장 큰 표면적이 큰 파일입니다. 아래는 라인 기준 코드 맵입니다.

### 8.1 핵심 함수 인덱스 (라인 번호 기준)

| 영역 | 함수 | 라인 |
|---|---|---|
| 탭 매니지먼트 | `openTab` / `setActive` / `closeTab` / `renderTabs` / `renderPanel` | 941, 950, 958, 971, 986 |
| 유틸 | `setStatus` / `showToast` / `destroyChart` | 998, 999, 1021 |
| 데이터 가공 | `sliceLastN` / `lastValidIdx` / `getLastIdx` / `fmtMonthShort` / `fmtMonthCompact` | 1029, 1060, 1067, 1072, 1078 |
| 통계 | `sumNum` / `avgNum` / `safeDiv` / `monthColor` | 1084, 1087, 1091, 1099 |
| 영속화 | `persistDashboardData` / `loadDashboardFromStorage` | 1109, 1118 |
| 인라인 편집 | `tabToolbar` / `bindTabToolbar` / `renderInlineEditTables` / `saveTabEdits` | 1140, 1154, 1182, 1277 |
| 사진 갤러리 | `renderPhotoGallery` / `editCaption` / `saveCaption` / `deletePhoto` | 2519, 2564, 2582, 2591 |
| 라이트박스 | `openLightbox` / `closeLightbox` / `navLightbox` | 2601, 2609, 2610 |
| 사진 영속화 | `persistPhotosData` / `loadPhotosFromStorage` | 2627, 2637 |
| 사진 업로드 | `handleFiles` / `renderUploadQueue` / `commitUploadQueue` / `renderUploadStats` / `reloadPhotosTabIfOpen` | 2781, 2803, 2822, 2859, 2881 |
| 사진 import/export | `exportPhotosData` / `importPhotosData` / `resetPhotosData` | 2889, 2900, 2921 |
| 마일스톤 | `_msQuarterOf` (이하 마일스톤 렌더) | 2936 |
| 편집 테이블 | `renderEditorTables` / `renderMilestonesTable` / `renderPlanTable` | 3213, 3297, 3318 |
| 편집 행 | `addMilestoneRow` / `addPlanRow` / `delRow` | 3335, 3339, 3343 |
| 편집 적용 | `setByPath` / `applyEdits` / `exportData` / `importData` / `resetData` | 3354, 3363, 3385, 3396, 3421 |
| 부트 | `openTab('overview')` | 3484 |

### 8.2 패널 렌더 컨벤션

각 탭 패널은 다음 두 객체에 등록됩니다:

```js
// HTML 문자열을 반환하는 함수
PANELS[key] = () => `<div class="grid">...</div>`;

// 렌더 후 차트/이벤트 바인딩
PANEL_INIT[key] = () => { /* Chart.js 인스턴스 생성 */ };
```

`renderPanel(key)` 가 두 함수를 순차 호출 → DOM 삽입 후 차트 초기화. 차트 인스턴스는 `charts[id]` 에 보관되어 재렌더 시 `destroyChart(id)` 로 해제.

### 8.3 데이터 흐름

```
[로드 시점]
  data.js          ─► window.DASHBOARD_DATA  ─┐
  photos.js        ─► window.PHOTOS_DATA      ├─► 패널 렌더
  localStorage     ─► loadDashboardFromStorage┘ (편집중인 임시본 우선)

[편집 흐름]
  사용자 인라인 편집 → window.DASHBOARD_DATA 즉시 변경
                    → persistDashboardData() (localStorage 저장)
                    → 패널/차트 재렌더
                    → (선택) JSON 내보내기 → data.js 교체 → git push

[차트 재렌더]
  setActive(key) → renderPanel(key) → destroyChart(*) → new Chart(...)
```

---

## 9. 데이터 추출 파이프라인 (Python)

> 월별 PPT가 새로 들어왔을 때만 사용. 평소 월간 데이터 갱신은 **데이터 편집 탭**으로 충분.

### 9.1 스크립트 책임 분리
| 스크립트 | 입력 | 출력 | 역할 |
|---|---|---|---|
| `extract_slides.py` | `ppt_extract/<MM월>/ppt/slides/*.xml` | `slides_data.json`, `slides_summary.txt` | PPT 텍스트/이미지 ref 추출 |
| `extract_photos_legacy.py` | 2023~2024 PPT 압축본 | `photos/YYYY-MM/*.jpg` | legacy 사진 추출 |
| `extract_legacy.py` | 2023~2024 PPT | `slides_data_legacy.json` | legacy 슬라이드 추출 |
| `extract_all_2023_2024.py` | legacy slides | `legacy_kpi_extracted.json` | 공정/안전/인력 KPI 추출 |
| `build_photo_manifest.py` | `slides_data.json` + `PHOTO_PAGES` 매핑 | `photos.js`, `photos_manifest.json` | 캡션 mapping 후 manifest 생성 |
| `merge_data.py` | 기존 `data.js` + `legacy_kpi_extracted.json` | 새 `data.js` | 38개월 통합 시계열 작성 |
| `merge_photos.py` | 1Q + legacy manifest | `photos.js` 통합 | 사진 매니페스트 머지 |

### 9.2 PowerShell에서 실행 시 주의 (UTF-8)
```powershell
$env:PYTHONIOENCODING="utf-8"   # cp949 인코딩 에러 우회
python extract_slides.py
python build_photo_manifest.py
```
> `merge_data.py:17` 의 `ROOT` 는 `C:\Users\14ZB95N\Desktop\대시보드` 로 하드코딩되어 있음 — **실행 전 본인 경로로 수정 필수**.

### 9.3 신규 월 추가 워크플로우 (PPT 기준)
1. PPT(DRM 해제본)를 로컬에 복사
2. `extract_slides.py` 의 `MONTHS` 배열에 새 월 추가
3. `build_photo_manifest.py` 의 `PHOTO_PAGES` 에 슬라이드별 캡션 매핑 추가 (수동 큐레이션)
4. `python extract_slides.py && python build_photo_manifest.py`
5. 생성된 `photos/<key>/` 와 `photos.js` 확인
6. 데이터 편집 탭에서 KPI 입력 → JSON 내보내기 → `data.js` 교체
7. `git add . && git commit && git push`

---

## 10. 상태 저장 & 영속화

| 저장소 | 키 | 용도 | 수명 |
|---|---|---|---|
| `localStorage` | `lng_dashboard_data_v1` | 인라인 편집 임시본 (DASHBOARD_DATA) | 영구(브라우저별) |
| `localStorage` | `lng_dashboard_photos_v1` | 캡션 수정/사진 업로드 임시본 | 영구(브라우저별) |
| `data.js` | `window.DASHBOARD_DATA` | 정식 데이터 (배포 대상) | git history |
| `photos.js` | `window.PHOTOS_DATA` | 정식 사진 매니페스트 | git history |

> 인라인 편집은 즉시 화면에 반영되지만 **`data.js` 자체는 변경되지 않음**. 정식 반영하려면 반드시 JSON 내보내기 → 파일 교체 → push.

### 페이지 이탈 가드
- 미저장 변경이 있을 때 `beforeunload` 이벤트로 경고 다이얼로그 (FR-7.5)

---

## 11. 빌드 / 배포

### 11.1 빌드 단계 = **없음**
- `package.json` 부재 / `node_modules/` 부재
- Cloudflare Pages 설정: Framework `None`, Build cmd 비움, Output dir `/`

### 11.2 배포 절차
```powershell
# 데이터/사진 변경 후
git add data.js photos.js photos/
git commit -m "월별 데이터 갱신 (YYYY-MM)"
git push origin main
# → Cloudflare Pages가 1~2분 내 자동 재배포
```

### 11.3 접근 제어 흐름
1. 사용자가 `https://lng-dashboard-xxxx.pages.dev` 접근
2. Cloudflare Access가 가로채 로그인 페이지 표시
3. 이메일 입력 → 6자리 OTP 메일 발송 (`noreply@notify.cloudflare.com`)
4. 화이트리스트 일치 시 24h 세션 발급 → 대시보드 진입
5. 미일치 시 “권한 없음” 페이지

자세한 설정은 [`DEPLOYMENT.md`](./DEPLOYMENT.md) 참고.

---

## 12. 개발 환경 설정

### 12.1 로컬 미리보기 (정적 서버)
빌드 도구가 없으므로 단순 정적 서버면 충분:
```powershell
# Python (권장 — 한글 폴더 지원)
$env:PYTHONIOENCODING="utf-8"
python -m http.server 8080
# → http://localhost:8080/index.html
```
또는 `index.html` 더블클릭 (단, `file://` 에선 일부 브라우저 보안정책으로 사진 로드 제한 가능 — 정적 서버 권장).

### 12.2 코드 편집
- 권장: VS Code (한국어 경로 정상 지원)
- 추천 확장: Live Server (자동 새로고침)
- 차트 디버깅: Chrome DevTools에서 `window.charts` 로 인스턴스 직접 조회

### 12.3 OneDrive 동기화 주의
이 폴더는 OneDrive 경로(`...OneDrive - POSCO INTERNATIONAL\바탕 화면\대시보드`) 안에 있습니다. **git 작업 중 OneDrive 동기화 충돌**이 발생할 수 있으므로:
- 작업 직전/직후 OneDrive 동기화 상태 확인
- 충돌이 빈번하면 `C:\Users\<user>\projects\lng-dashboard\` 등 OneDrive 외부로 이동 권장

---

## 13. 확장 가이드

### 13.1 신규 월 데이터 추가
1. `data.js` 에서 모든 시계열의 `months` 배열에 새 월 push
2. 각 시계열 배열에 동일 길이로 값 추가 (값 없음은 `null`)
3. `project.data_gaps` 정합성 확인
4. 브라우저 새로고침으로 검증

### 13.2 신규 공구 추가 (예: “부두-2”)
영향 범위가 크므로 다음을 모두 수정:
- `data.js`: `progress / manpower / no_accident_days` 에 키 추가
- `data.js`: `incident_summary` 에 row 추가
- `index.html`: 공구 셀렉터(공정 관리 탭), 안전 카드, 차트 색상 매핑
- `photos.js`: 해당 공구의 `category` 값 사용

### 13.3 신규 KPI 추가
1. `data.js` 에 새 섹션 추가 (`{ months, ...series }` 패턴 따름)
2. `index.html` 의 `PANELS.<tab>` 함수에 카드/차트 마크업 추가
3. `PANEL_INIT.<tab>` 에 Chart.js 인스턴스 생성 코드 추가
4. `renderInlineEditTables` 에 편집 항목 추가 (편집 가능하게 하려는 경우)

### 13.4 차트 추가 패턴
```js
PANELS.myTab = () => `
  <div class="card col-6">
    <h3>새 차트</h3>
    <canvas id="myChart"></canvas>
  </div>
`;

PANEL_INIT.myTab = () => {
  destroyChart('myChart');
  const ctx = document.getElementById('myChart').getContext('2d');
  charts['myChart'] = new Chart(ctx, {
    type: 'line',
    data: { labels: [...], datasets: [...] },
    options: { responsive: true, maintainAspectRatio: false }
  });
};
```

---

## 14. 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| 차트가 안 보임 | Chart.js CDN 차단 — 사내망 프록시 확인. `window.Chart` 가 정의되었는지 콘솔 확인 |
| 한글이 깨져 보임 | `<meta charset="UTF-8">` 확인. PowerShell 실행 시 `$env:PYTHONIOENCODING="utf-8"` 설정 |
| 사진이 안 보임 | `file://` 로 열었거나 경로 대소문자 불일치. 정적 서버로 실행하고 `photos/<key>/<file>` 경로 검증 |
| 편집 후 새로고침했더니 원본 | localStorage 정상. JSON 내보내기 후 `data.js` 미교체 상태 확인 |
| `git push` 시 인증 실패 | GitHub PAT(`repo` 권한) 발급 후 비밀번호 자리에 입력 |
| Cloudflare OTP 메일 미수신 | 스팸함 확인. 발신: `noreply@notify.cloudflare.com` |
| 차트가 갑자기 늘어나거나 깨짐 | 동일 canvas에 두 번 `new Chart` — `destroyChart` 누락. `index.html:1021` 패턴 따랐는지 확인 |
| `merge_data.py` 실행 시 경로 에러 | `ROOT` 변수 (스크립트 17번째 줄) 본인 경로로 수정 |
| OneDrive 동기화로 git 충돌 | 작업 디렉터리를 OneDrive 외부로 이동 |

---

## 15. 부록 — 용어 / 명명 규칙

### 15.1 용어 사전
| 용어 | 정의 |
|---|---|
| 공구 (工區) | 공사 분할 단위 — 육상부 / 해상부 / 154kV |
| 공정률 | 계획 대비 실적 진척률 (%) |
| 본계약 / 1차계약 | 사업 발주 단계 — 1차계약(2023-02~07) → 본계약(2023-08~) |
| Near Miss | 사고로 이어질 뻔한 아차사고 (`일반NearMiss`, `중대NearMiss` 두 분류) |
| 무재해 일수 | 마지막 재해일로부터의 누적 일수 |
| S-curve | 누적 공정률 곡선 — 계획 vs 실적 비교 |
| 지적사항 | 안전 점검에서 적발된 위험 요소 — 9개 분류 |
| KOGAS | 발주처(한국가스공사). 본 대시보드 외부 |

### 15.2 명명 규칙
- **월 키**: `YYYY-MM` (ISO) — 단, 1Q 사진 폴더는 단축표기 `01월/02월/03월` 호환
- **공구 키**: `종합 / 육상부 / 해상부 / 154kV` (한글 고정, 코드 곳곳 lookup)
- **공종**: 토목 / 기계 / 전기 / 건축 / 부두공 / 기타
- **상태**: 착수 / 진행 / 완료 (마일스톤)
- **차트 ID**: 패널 키 + 의미 (예: `chartProgressLand`, `chartManpowerStacked`)

### 15.3 라이선스 / 저작권
- 본 코드는 사내 비공개 자산. POSCO INTERNATIONAL 에너지건설 TF 소유
- Chart.js (MIT), Pretendard (OFL) 외부 의존만 오픈소스

---

## 변경 이력

| 버전 | 일자 | 변경 |
|---|---|---|
| 1.0 | 2026-04 | 최초 README (개요 중심) |
| 1.1 | 2026-05 | **개발자용 설계서로 전면 재작성** — 구조/코드맵/데이터 모델/추출 파이프라인 상세화 |

---

© 2026 POSCO INTERNATIONAL — 에너지건설 TF
연락 / 접근 신청: **kyungtae@poscointl.com**
