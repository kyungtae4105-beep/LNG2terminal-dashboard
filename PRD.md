# PRD — 광양 제2 LNG터미널 증설공사 주요 지표 Dashboard

> **Product Requirements Document**
> 작성: POSCO INTERNATIONAL 에너지건설 TF
> 버전: v1.0 (2026-04)
> 관련 문서: [BRD.md](./BRD.md), [README.md](./README.md), [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 1. 개요

### 1.1 제품명
광양 제2 LNG터미널 증설공사 주요 지표 Dashboard (`lng-dashboard`)

### 1.2 한 줄 정의
공정·인력·안전·마일스톤·현장사진을 단일 정적 웹 페이지에서 통합 시각화하는 임직원 전용 대시보드.

### 1.3 핵심 가치 제안
- **빌드리스(Buildless)** — `index.html` 더블클릭 또는 Cloudflare Pages 직접 서빙
- **편집 가능 데이터** — 브라우저 UI에서 인라인 수정 → JSON 내보내기 → git push
- **사진까지 한 곳에** — 분기별 PPT에 흩어진 작업사진 112장을 월/공종 필터로 통합 열람

---

## 2. 사용자 정의 (Personas)

### P1. 임원 / 본부장 (Executive Viewer)
- **목표**: 5분 내에 종합 공정률·안전·주요 마일스톤 파악
- **주요 화면**: 종합 대시보드, 마일스톤
- **편집 권한**: 없음 (읽기 전용 사용)

### P2. 현장 PM / 공종 책임자 (Site Manager)
- **목표**: 자기 공구의 상세 추이·인력·지적사항 추적
- **주요 화면**: 공정 관리, 시공/자원관리, 안전 관리, 월별 작업사진
- **편집 권한**: 데이터 입력자에게 갱신 요청

### P3. 데이터 입력자 (Data Editor — TF 실무)
- **목표**: 매월 5일까지 전월 데이터 갱신·검증·배포
- **주요 화면**: 데이터 편집 탭
- **편집 권한**: 전체 인라인 수정, JSON 내보내기/불러오기

### P4. 시스템 관리자 (Access Admin)
- **목표**: 신청 메일 검토 → 화이트리스트 등록, 접근 로그 점검
- **사용 도구**: Cloudflare Zero Trust 콘솔
- **편집 권한**: 사용자 관리

---

## 3. 사용자 시나리오

### S1. 월간 임원 보고
> 본부장이 보고 직전 대시보드를 열어 종합 게이지·S-curve·마일스톤만 빠르게 훑고, 안전 지적사항을 클릭하여 추세를 확인한다. **PPT 재가공 없이 화면을 그대로 공유**한다.

### S2. 공구별 비교 분석
> 육상부 PM이 자기 공구 vs 종합 평균을 한 화면에서 비교하고, 편차가 큰 월의 인력 변동을 인력 탭에서 확인한다.

### S3. 데이터 갱신 (월말)
> TF 실무자가 PPT 보고서를 받은 후 **데이터 편집** 탭에서 4월 컬럼을 추가·입력 → JSON 내보내기 → `data.js` 교체 → `git push`. Cloudflare Pages가 1~2분 내 재배포.

### S4. 신규 사용자 등록
> 유관 부서 직원이 `kyungtae@poscointl.com`로 접근 신청 메일 발송 → 관리자가 Zero Trust에서 이메일 추가 → 즉시 OTP 로그인 가능.

### S5. 사진 검색
> 안전 담당이 "3월 해상부 부두공" 작업사진을 확인하기 위해 **월별 작업사진** 탭에서 월/공종 필터 적용 → 라이트박스로 캡션과 함께 열람.

---

## 4. 기능 요구사항

### 4.1 화면(탭) 구성

| # | 탭 | 핵심 컴포넌트 |
|---|---|---|
| T1 | **종합 대시보드** | 진행률 게이지, S-curve(계획/실적), KPI 카드, 인력 요약, 안전 요약, 교육 요약 |
| T2 | **공정 관리** | 공구별(종합/육상/해상/154kV) 월별 공정률 라인차트 + 계획/실적 편차 테이블 |
| T3 | **시공/자원관리** | 공구별 인력 stacked bar (관리자/협력사) + 비율 표 |
| T4 | **안전 관리** | 무재해 일수 카드 / Near Miss·재해 요약 / 지적사항 분류(9종) 추이 / 교육(4종) 추이 |
| T5 | **월별 작업사진** | 월(1·2·3월)·공종 필터 + 썸네일 그리드 + 라이트박스(캡션 포함) |
| T6 | **마일스톤** | 1Q 실적 일정표(완료/착수) + 차월 계획 일정표 |
| T7 | **데이터 편집** | 모든 지표 인라인 입력, JSON 내보내기, JSON 불러오기 |

### 4.2 기능 명세 (FR)

#### FR-1. 종합 대시보드
- **FR-1.1** 종합 공정률(최신월) 게이지 표시 — 계획/실적 동시 표기
- **FR-1.2** S-curve 라인차트 — 종합 공구의 월별 계획·실적 비교
- **FR-1.3** KPI 카드 — 종합 공정률, 누적 인력, 무재해 최대일수, 재해 합계
- **FR-1.4** 안전·교육 요약은 최신월 값 기준 카드로 표기

#### FR-2. 공정 관리
- **FR-2.1** 공구 선택 토글 (종합/육상부/해상부/154kV) 또는 4공구 동시 비교
- **FR-2.2** 라인차트: x축=월, y축=공정률(%) — 계획선·실적선 2종
- **FR-2.3** 편차 테이블: 월별 (실적 − 계획), 음수는 적색 강조

#### FR-3. 시공/자원관리
- **FR-3.1** Stacked bar — 관리자(상단) + 협력사(하단)
- **FR-3.2** 월별 관리자/협력사 비율(%) 보조 표시

#### FR-4. 안전 관리
- **FR-4.1** 공구별 무재해 일수 카드(최신월 기준), 미입력은 "—" 표시
- **FR-4.2** 재해 요약 표 — 공상/일반재해/중대재해/일반NearMiss/중대NearMiss × 공구
- **FR-4.3** 육상부 지적사항 9분류(추락/전도/낙하·비래/감전/충돌·협착/붕괴·도괴/화재·폭발/질식/기타) 월별 라인차트
- **FR-4.4** 안전 교육 4종(채용·작업변경/특별/관리감독자/정기) 월별 stacked area

#### FR-5. 월별 작업사진
- **FR-5.1** 월 필터: 전체 / 1월 / 2월 / 3월
- **FR-5.2** 공종 필터: 토목/기계/전기/건축/부두공/기타
- **FR-5.3** 썸네일 그리드 (반응형, 최소 4열)
- **FR-5.4** 클릭 시 라이트박스 — 원본 + 캡션, ←/→ 키 네비게이션, ESC 닫기

#### FR-6. 마일스톤
- **FR-6.1** 1Q 실적 — 날짜순 정렬, 공종/공구/제목/상태(착수·완료) 컬럼
- **FR-6.2** 차월 계획 — 날짜순 정렬, 공종/제목 컬럼
- **FR-6.3** 상태별 색상 — 완료(녹색), 착수(청색)

#### FR-7. 데이터 편집
- **FR-7.1** 전 지표 인라인 셀 편집(숫자 검증)
- **FR-7.2** 행 추가/삭제(마일스톤·차월계획)
- **FR-7.3** **JSON 내보내기** — 현재 상태를 `window.DASHBOARD_DATA` 형태 JSON 파일로 다운로드
- **FR-7.4** **JSON 불러오기** — 파일 업로드 시 즉시 화면 반영(저장은 git push 시점)
- **FR-7.5** 미저장 변경 시 페이지 이탈 경고

#### FR-8. 접근 제어
- **FR-8.1** Cloudflare Access 게이트 — 미인증 시 로그인 페이지로 리디렉션
- **FR-8.2** 이메일 OTP 인증 — 6자리 코드, 24시간 세션
- **FR-8.3** 화이트리스트 외 이메일 차단

---

## 5. 데이터 모델

### 5.1 `window.DASHBOARD_DATA` 스키마

```ts
{
  project: {
    name: string,           // "광양 제2 LNG터미널 증설공사"
    owner: string,          // "에너지건설 TF"
    report_period: string,  // "2026년 1월 ~ 3월"
    purpose: string
  },

  progress: {
    months: string[],       // ["2026-01", "2026-02", "2026-03"]
    종합:   { plan: number[], actual: number[] },
    육상부: { plan: number[], actual: number[] },
    해상부: { plan: number[], actual: number[] },
    "154kV": { plan: number[], actual: number[] }
  },

  manpower: {
    months: string[],
    종합/육상부/해상부/154kV: { manager: number[], partner: number[] }
  },

  no_accident_days: {
    months: string[],
    육상부/해상부/154kV: (number|null)[]   // null = 미입력
  },

  safety_audit_land: {
    months: string[],
    추락/전도/낙하·비래/감전/충돌·협착/붕괴·도괴/화재·폭발/질식/기타: number[]
  },

  safety_edu_land: {
    months: string[],
    채용·작업변경/특별교육/관리감독자/정기교육: number[]
  },

  incident_summary: [
    { sub: string, 공상: number, 일반재해: number, 중대재해: number,
      일반NearMiss: number, 중대NearMiss: number }
  ],

  milestones: [
    { date: "YYYY-MM-DD", sub: string, 공종: string, title: string,
      status: "착수" | "완료" }
  ],

  next_month_plan: [
    { date: "YYYY-MM-DD", 공종: string, title: string }
  ]
}
```

### 5.2 사진 매니페스트 (`photos.js`)
- `window.PHOTO_MANIFEST = [{ month, 공종, file, caption }, ...]`
- 빌드 시 `extract_slides.py` → `build_photo_manifest.py` 파이프라인으로 생성
- 원본 PPT는 `.gitignore` 처리, 추출된 이미지(`photos/01월/`, `02월/`, `03월/`)만 commit

---

## 6. 비기능 요구사항 (NFR)

| 분류 | 요구사항 | 측정/검증 |
|---|---|---|
| 성능 | 첫 화면 LCP ≤ 3s (브로드밴드) | Chrome DevTools Lighthouse |
| 성능 | 사진 그리드 lazy-load, 스크롤 시 60fps | 프레임 드롭 ≤ 5% |
| 가용성 | Cloudflare Pages SLA 의존 (99.99%) | 배포 모니터링 |
| 보안 | 전 구간 HTTPS, OTP 인증, 화이트리스트 | Cloudflare Access 정책 |
| 보안 | `_headers` 로 보안 헤더 설정 | 배포본 검증 |
| 호환성 | Chrome/Edge ≥ 최근 2버전, Safari ≥ 최근 2버전 | 수동 QA |
| 반응형 | 1280×800 ~ 1920×1080 데스크톱 우선, 1024px 태블릿 가독 | 수동 QA |
| 접근성 | 키보드 탭 이동, alt 텍스트(사진 캡션) | WCAG 2.1 A 수준 지향 |
| 유지보수 | 빌드 도구 0개, CDN 의존(Chart.js)만 허용 | `package.json` 부재 유지 |

---

## 7. 시스템 아키텍처

### 7.1 구성도
```
[사용자 브라우저]
      │ HTTPS
      ▼
[Cloudflare Access 게이트] ─ (이메일 OTP + 화이트리스트)
      │ 인증 통과
      ▼
[Cloudflare Pages]  ◀── git push (main) ── [GitHub Private Repo]
      │
      ├─ index.html  (단일 페이지, Chart.js CDN)
      ├─ data.js     (지표 데이터 — 편집/배포 대상)
      ├─ photos.js   (사진 매니페스트)
      └─ photos/**   (작업사진 정적 자산)
```

### 7.2 기술 스택
- **Frontend**: HTML5, CSS3, ES6 JavaScript (프레임워크 없음)
- **차트**: Chart.js v4 (CDN: `cdn.jsdelivr.net/npm/chart.js@4.4.1`)
- **호스팅**: Cloudflare Pages (자동 배포 — main branch)
- **인증**: Cloudflare Access (Zero Trust, Email OTP)
- **데이터 추출 도구**: Python 3 (`python-pptx` 등) — 1회성 / 사진 갱신 시
- **VCS**: Git + GitHub Private Repo

### 7.3 배포 파이프라인
1. 로컬에서 데이터/사진 변경
2. `git commit && git push origin main`
3. Cloudflare Pages 자동 빌드 (build cmd 없음, 정적 서빙) — 1~2분
4. 라이브 도메인(`*.pages.dev`)에 즉시 반영

---

## 8. UX 가이드라인

### 8.1 디자인 원칙
- **VS Code-스타일 다크 테마** (배경 `#1e1e1e`, 보조 `#252526`, 강조 흰색)
- **좌측 Activity Bar + Sidebar + Main** 3분할 레이아웃
- **타이틀바**는 macOS 신호등 스타일 컨트롤 + 메뉴
- 차트 색상: 공구별 일관된 팔레트 유지 (육상=청색, 해상=청록, 154kV=주황)

### 8.2 인터랙션
- 탭 전환은 즉시 (페이지 리로드 없음)
- 차트 hover 시 툴팁(월·값·공구)
- 사진 라이트박스: ←/→ 키, ESC 닫기, 배경 클릭 닫기
- 데이터 편집 셀: Tab/Enter 이동, 잘못된 입력 시 적색 테두리

### 8.3 상태 표시
- 데이터 미입력: `—` (em dash)
- 마일스톤 상태: 완료=녹색 칩, 착수=청색 칩
- 편차 음수: 적색, 양수: 회색

---

## 9. 운영 / 유지보수

### 9.1 월간 데이터 갱신 절차 (5분 SLA)
1. **데이터 편집** 탭에서 새 월 컬럼 추가 + 값 입력
2. **JSON 내보내기** → 다운로드된 JSON으로 `data.js` 의 `window.DASHBOARD_DATA` 교체
3. `git add data.js && git commit -m "데이터 갱신 (4월)" && git push`
4. Cloudflare Pages 재배포 확인

### 9.2 월간 사진 갱신 절차
1. 새 PPT를 로컬에 위치
2. `python extract_slides.py` 실행 → `slides_data.json` / `ppt_extract/` 생성
3. `python build_photo_manifest.py` 실행 → `photos/MM월/` + `photos.js` 갱신
4. git commit & push

### 9.3 사용자 관리 (관리자 전용)
| 작업 | 경로 |
|---|---|
| 신규 사용자 추가 | Zero Trust → Access → Applications → `LNG Dashboard` → Policy → 이메일 추가 |
| 권한 회수 | 위와 동일 경로에서 이메일 삭제 |
| 접근 로그 확인 | Zero Trust → Logs → Access |

---

## 10. 검증 / Acceptance

### 10.1 기능 검증 체크리스트
- [ ] 7개 탭이 모두 정상 렌더링되며, 데이터가 정확히 표시됨
- [ ] 공정/인력/안전 차트의 hover 툴팁이 정확한 값을 표시
- [ ] 데이터 편집 후 JSON 내보내기 → 재 import 시 값이 정확히 복원
- [ ] 사진 라이트박스가 ←/→/ESC 키로 정상 동작
- [ ] 마일스톤 상태 색상이 정의대로 적용
- [ ] 미승인 이메일은 접근 차단, 승인 이메일은 OTP 로그인 성공

### 10.2 성능 검증
- [ ] 첫 화면 로딩 ≤ 3초 (Lighthouse Performance ≥ 80)
- [ ] 사진 탭 스크롤 시 끊김 없음 (lazy-load 동작)

### 10.3 보안 검증
- [ ] HTTPS 강제 / `_headers` 적용 확인
- [ ] 비공개 GitHub repo 유지
- [ ] OneDrive 동기화에 의한 secret 노출 없음 (`.gitignore` 검증)

---

## 11. 향후 개선 (Backlog)

| ID | 항목 | 우선순위 |
|---|---|---|
| BL-01 | 사용자 정의 도메인 (예: `lng.posco-international.com`) | Med |
| BL-02 | PDF 내보내기 (탭 단위 인쇄 최적화) | Med |
| BL-03 | 4월~ 데이터 누적 시 분기·반기 비교 뷰 | Med |
| BL-04 | 모바일(스마트폰) 반응형 강화 | Low |
| BL-05 | 변경 이력 자동 기록(누가 언제 어떤 값을 변경) | Low |
| BL-06 | 사내 SSO(Azure AD) 연동 검토 | Low |
| BL-07 | 안전 지표 임계치 경보 (Near Miss 급증 등) | Low |

---

## 12. 변경 이력

| 버전 | 일자 | 작성/변경 | 내용 |
|---|---|---|---|
| 0.1 | 2026-03 | TF | 과제정의서 초안 (PPT) |
| 1.0 | 2026-04-30 | TF | PRD v1 정식화 — 1Q 데이터 적재본 기준 |

---

© 2026 POSCO INTERNATIONAL — 에너지건설 TF
