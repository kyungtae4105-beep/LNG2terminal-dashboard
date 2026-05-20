# Fallback — SharePoint / SPFx 전환 시나리오

> **대상 독자**: DX기획·운영그룹, 박경태 대리
> **목적**: Cloudflare Access + Entra ID 적용이 사내 정책/일정상 어려운 경우의 **대안 경로**(SharePoint/SPFx)와, 본 저장소의 코드 구조가 그 전환을 어떻게 흡수하도록 설계되어 있는지 정리.
> **선행 문서**: `docs/ACCESS_CONSOLE_SETUP.md`, `docs/TEAMS_APP_REGISTRATION.md`

---

## 1. 언제 이 문서를 펼쳐야 하는가

다음 중 하나라도 해당되면 SharePoint 전환을 **검토**한다.

| 트리거 | 설명 |
|---|---|
| IT보안팀이 외부 SaaS(Cloudflare) IdP 연결을 거부 | Entra ID 앱 등록 자체가 보류 |
| `ACCESS_CONSOLE_SETUP.md` ⑥-3의 점검을 모두 거쳤는데도 Teams 임베드 실패 | 모바일 third-party cookie 정책 등 통제 불가 사유 |
| 사내 M365 정책 정합성이 최우선 가치 | 데이터 거버넌스/감사 기록을 M365 안에서 일원화해야 함 |
| 데이터 편집 권한을 SharePoint 권한으로 일원화하려는 운영 요구 | 현재 코드 측 "편집 비밀번호" 보다 권한 모델이 강함 |

> 위 사유가 **없다면** Cloudflare Access 경로가 단기 적용성과 코드 수정 범위 면에서 우월하다. 본 문서는 어디까지나 **Plan B**.

---

## 2. 데이터 구조 전환 매핑

기존 정적 자산이 SharePoint 어느 자원으로 매핑되는지의 1:1 대응 표.

| 항목 | 현재 (정적) | 전환 방향 |
|---|---|---|
| KPI 데이터 | `data.js` (window.DASHBOARD_DATA) | **SharePoint List** 또는 Excel/JSON 파일을 문서 라이브러리에 저장 |
| 작업사진 | `photos/` 폴더 + `photos.js` (window.PHOTOS_DATA) | **SharePoint 문서 라이브러리** (월별 폴더 구조 그대로 이관) |
| 사용자 권한 | (없음 — Cloudflare Access 정책으로 통제) | **SharePoint 사이트 권한** (소유자/구성원/방문자 그룹) |
| Teams 연계 | Teams 앱 manifest + iframe | **SharePoint 페이지를 Teams 채널 탭으로 추가** (Teams 기본 기능) |
| 운영자 편집 | 코드 측 "편집 비밀번호" 모달 | **SharePoint 권한 기반** (소유자/구성원 그룹의 List 편집 권한) |
| 이메일 표시 | Cloudflare Access `Cf-Access-Authenticated-User-Email` | SPFx Context (`this.context.pageContext.user.email`) |

---

## 3. 난이도 비교

두 경로의 정성 비교 — 의사결정용 한 장 요약.

| 구분 | Cloudflare Access + Entra ID | SharePoint / SPFx |
|---|---|---|
| 기존 앱 수정 범위 | **낮음** (CSP/메타/배지 정도) | **중간~높음** (데이터 어댑터 + 빌드 파이프라인 추가) |
| 현업 단독 처리 가능성 | 낮음 (DX/IT 협조 필요) | 낮음 (DX/IT 협조 필요) |
| DX운영/IT 지원 필요 | 필요 | 필요 |
| URL 공개 문제 해결 | 가능 | 가능 (SharePoint URL 자체가 권한 기반) |
| Teams 연계성 | 좋음 (iframe + Access SSO) | 좋음 (Teams 채널 탭 네이티브) |
| 사내 M365 정책 정합성 | **중간** (외부 SaaS 의존) | **높음** (M365 내부 완결) |
| 단기 적용성 | **상대적으로 빠름** | 시간이 더 필요 (List 스키마 설계 + SPFx 빌드/배포) |
| 장기 운영 안정성 | 좋음 | **매우 좋음** (M365 라이프사이클에 동기화) |
| 라이선스 / 비용 | Cloudflare Free 50명 / 초과시 PAYG | M365 라이선스 내 (추가 비용 없음) |
| 감사 로그 | Zero Trust Logs | M365 통합 감사 로그 |

> **결론 한 줄**: "빠르게 닫고 운영하려면" Cloudflare Access. "M365 정책에 완전히 녹이려면" SharePoint.

---

## 4. 코드 측 어댑터(A-5)와의 매핑

본 저장소는 SharePoint 전환을 **부분적으로 흡수**할 수 있도록 데이터 접근 지점을 한 곳으로 격리해 두었다.

### 4-1. 어댑터 위치
`assets/data-source.js` — `window.DATA_SOURCE` 객체 하나가 모든 데이터 접근을 위임받는다.

### 4-2. 현재 (정적) 구현
```js
// assets/data-source.js 발췌
function _kpiRoot()    { return window.DASHBOARD_DATA || {}; }
function _photosRoot() { return window.PHOTOS_DATA    || {}; }

DATA_SOURCE.getKPI       = () => _kpiRoot();
DATA_SOURCE.getPhotos    = () => _photosRoot();
DATA_SOURCE.getKPIAsync  = () => Promise.resolve(_kpiRoot());
DATA_SOURCE.getPhotosAsync = () => Promise.resolve(_photosRoot());
```

### 4-3. SharePoint 전환 시 교체 예시 (개념 수준 — 본 PR에는 미포함)

KPI → SharePoint List:
```js
async function _kpiRootSharePoint() {
  // Graph API:  GET /sites/{siteId}/lists/{listId}/items?expand=fields
  // SPFx 환경: this.context.msGraphClientFactory ...
  // 또는 SP REST: /_api/web/lists/getbytitle('KPI')/items
  const items = await graph.api(`/sites/${siteId}/lists/${listId}/items`)
                          .expand('fields').get();
  return normalizeKPI(items.value); // 기존 DASHBOARD_DATA 와 동일 shape 으로 정규화
}
```

작업사진 → SharePoint 문서 라이브러리:
```js
async function _photosRootSharePoint() {
  // GET /sites/{siteId}/drives/{driveId}/root/children
  const children = await graph.api(`/sites/${siteId}/drives/${driveId}/root/children`).get();
  return groupPhotosByMonth(children.value);
}
```

> 핵심: 어댑터 인터페이스(`getKPI`/`getPhotos`/`getKPIAsync`/`getPhotosAsync`)는 동일 유지. 호출부(index.html 의 차트/렌더 코드)는 **수정 없음**.

### 4-4. 정규화 어댑터의 책임

전환 시 가장 중요한 작업은 **shape 정규화**이다. 기존 `DASHBOARD_DATA` 구조를 SharePoint List 컬럼에서 재구성해 동일한 키 이름으로 노출.

| 호출부 기대 키 | SharePoint List 컬럼 (예시) |
|---|---|
| `month` | `fields.Month` (yyyy-MM) |
| `progressPlan` | `fields.PlanPercent` (Number) |
| `progressActual` | `fields.ActualPercent` (Number) |
| `safety.LTI` | `fields.LTI` (Number) |
| `milestones[].title` | `fields.MilestoneTitle` (Text) |
| ... | ... |

이 매핑 표를 SharePoint List 설계 시 **단일 진실 원천**으로 사용한다.

---

## 5. 단계별 마이그레이션 로드맵

Cloudflare Access 운영 중에 SharePoint 로 이행해야 할 경우의 권장 순서.

### 5-1. 준비 단계 (1~2주)
- SharePoint 사이트 신규 생성 (Communication site 권장)
- KPI List 스키마 설계 + 시범 데이터 1개월치 입력
- 문서 라이브러리 생성 + 월별 폴더 1개월치 사진 업로드
- 사이트 권한 그룹 정의 (소유자/편집자/뷰어)

### 5-2. 어댑터 교체 단계 (1주)
- `assets/data-source.js` 에 SharePoint 어댑터 추가
- 환경 분기로 두 어댑터를 토글 (`DATA_SOURCE.kind === 'sharepoint'`)
- 정규화 함수 단위 테스트 (기존 `data.js` 와 동일 shape 보장)

### 5-3. 호스팅 전환 단계 (1~2주)
- 옵션 A: 정적 사이트는 Pages 유지, 데이터만 SharePoint API 호출 (Access 또는 Pages Functions JWT 검증 추가)
- 옵션 B (권장): **SPFx 웹파트** 로 재패키징 → SharePoint 페이지에 임베드 → Teams 탭으로 노출
  - 빌드: `yo @microsoft/sharepoint` → React/HTML 마이그레이션 → `gulp bundle --ship && gulp package-solution --ship`
  - 배포: 앱 카탈로그에 `.sppkg` 업로드 → 사이트 추가 → Teams 탭 추가

### 5-4. 폐기 단계
- Cloudflare Access Application 비활성화 (또는 Audit 모드 1개월 유지 후 삭제)
- Entra ID 앱 등록은 SPFx 가 사용할 수 있으므로 **즉시 삭제하지 말고** 권한만 재정의

---

## 6. 의사결정 체크리스트 — "지금 SharePoint로 가야 하나?"

| 질문 | YES → SharePoint 검토 | NO → Cloudflare Access 유지 |
|---|---|---|
| IT보안팀이 Cloudflare 외부 SaaS 사용을 거부했는가? | ☐ | ☐ |
| Teams 모바일에서 1주일 이상 임베드 실패가 지속되는가? | ☐ | ☐ |
| 데이터 편집 권한을 사이트 권한으로 일원화해야 하는가? | ☐ | ☐ |
| M365 감사 로그로 모든 접근 기록을 일원 관리해야 하는가? | ☐ | ☐ |
| 향후 6개월 내 SharePoint 사이트 신설 계획이 이미 있는가? | ☐ | ☐ |

> 2개 이상 YES → SharePoint 전환을 정식 안건으로 상정.
> 1개 이하 YES → Cloudflare Access 유지하며 분기별 재검토.

---

## 7. 관련 문서

- `docs/ACCESS_CONSOLE_SETUP.md` — 1순위 경로 (Cloudflare Access + Entra ID)
- `docs/TEAMS_APP_REGISTRATION.md` — Teams 패키지/SSO 흐름
- `assets/data-source.js` — 본 문서 4장의 어댑터 실제 코드
