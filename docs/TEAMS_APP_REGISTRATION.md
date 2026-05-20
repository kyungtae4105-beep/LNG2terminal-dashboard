# Teams 앱 등록 — manifest와 Cloudflare Access 연결 가이드

> **대상 독자**: DX운영그룹 (Teams 앱 등록 담당) / 박경태 대리
> **목적**: 이미 작성된 Teams 앱 패키지(`teams-app/manifest.json`)와 Cloudflare Access 적용 후의 동작 흐름을 한 번에 이해할 수 있도록 정리.
> **사전 조건**: `docs/ACCESS_CONSOLE_SETUP.md` 의 ①~⑤ 단계가 완료되어 있어야 함.

---

## 1. 패키지 구성 한눈에 보기

저장소 안에는 Teams 앱 패키지가 **2종** 준비되어 있다.

| 폴더 | 용도 | 특징 |
|---|---|---|
| `teams-app/` | **운영 패키지** | URL이 `https://energytf-dashboard.pages.dev/` 로 확정 |
| `teams-app-team-channel/` | **템플릿** (배포처 미확정용) | `REPLACE-WITH-CLOUDFLARE-PAGES-HOST` placeholder |

운영 등록 시 `teams-app/` 을 zip 으로 묶어 사용한다. (zip 명: `LNG2_Dashboard_Teams_FINAL.zip`)

---

## 2. manifest.json 핵심 필드 가이드

`teams-app/manifest.json` 에서 Access 적용과 연관된 핵심 필드는 다음과 같다.

### 2-1. `staticTabs[].contentUrl` / `websiteUrl`
```json
"staticTabs": [
  {
    "entityId": "lng2-dashboard-main",
    "name": "Dashboard",
    "contentUrl": "https://energytf-dashboard.pages.dev/",
    "websiteUrl": "https://energytf-dashboard.pages.dev/",
    "scopes": ["personal", "team", "groupChat"]
  }
]
```

- **contentUrl**: Teams 탭 안의 iframe 이 실제로 로드하는 URL. 본 URL은 Cloudflare Access 의 보호 도메인 (④의 Application domain) 과 **정확히 일치**해야 한다.
- **websiteUrl**: "브라우저에서 열기" 버튼이 사용하는 URL. 동일 URL 권장.
- **scopes**: `personal` (개인 탭), `team` (채널 탭), `groupChat` (그룹 채팅 탭) — 3종 모두 허용.

### 2-2. `validDomains`
```json
"validDomains": [
  "energytf-dashboard.pages.dev",
  "cdn.jsdelivr.net",
  "fonts.googleapis.com",
  "fonts.gstatic.com",
  "res.cdn.office.net"
]
```

- Teams JS SDK 가 iframe 내부에서 **이동을 허용**하는 도메인 화이트리스트.
- **Cloudflare Access 리다이렉트 흐름** (`*.cloudflareaccess.com`) 은 보통 **추가 불필요**.
  이유: Access 가 보호 도메인 → 인증 도메인 → 보호 도메인 으로 **전체 페이지 리다이렉트**를 처리하는데, 이는 Teams JS 의 internal navigation 정책 대상이 아니며 브라우저 레벨에서 진행되기 때문.
- 단, 만약 특정 환경(주로 모바일 Teams 일부 버전)에서 차단되는 사례가 발견되면 다음을 추가 검토:
  ```json
  "*.cloudflareaccess.com",
  "*.login.microsoftonline.com"
  ```

### 2-3. `permissions`
```json
"permissions": ["identity"]
```
- `identity`: Teams 컨텍스트(테넌트/사용자 정보) 접근. 본 대시보드는 사용자 이메일을 Cloudflare Access 측에서 받아 표시하므로 Teams identity 권한은 **표시 외 기능에는 미사용**.

---

## 3. Access 적용 후 Teams SSO 동작 원리

### 3-1. 텍스트 다이어그램 (최초 1회 인증)

```
[Teams 데스크탑/웹/모바일]
      │
      │ 사용자가 Dashboard 탭 클릭
      ▼
┌──────────────────────────────────────────────────┐
│  Teams iframe                                    │
│  src = https://energytf-dashboard.pages.dev/     │
└──────────────────────────────────────────────────┘
      │
      │ (1) HTTP GET — CF_Authorization 쿠키 없음
      ▼
[Cloudflare Access]
      │
      │ (2) 302 → https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
      ▼
[Microsoft Entra ID 로그인 페이지]
      │
      │ (3) 사용자가 회사 계정으로 로그인 (또는 기존 세션으로 SSO)
      │     ※ Teams 가 이미 회사 계정으로 로그인되어 있다면
      │       대부분 클릭 없이 자동 통과 (Single Sign-On)
      ▼
[Entra ID]
      │
      │ (4) 인증 토큰 → 302 → https://energytf.cloudflareaccess.com/cdn-cgi/access/callback
      ▼
[Cloudflare Access]
      │
      │ (5) Policy 평가 (⑤ Allow 매칭) → CF_Authorization 쿠키 발급
      │     Set-Cookie: CF_Authorization=...; SameSite=None; Secure; Domain=...
      │     ← ★ SameSite=None / Secure 가 핵심 (Teams iframe 호환)
      │
      │ (6) 302 → https://energytf-dashboard.pages.dev/
      ▼
[Cloudflare Pages]
      │
      │ (7) 정적 자산(index.html, data.js 등) 응답
      ▼
[Teams iframe 안에 대시보드 렌더링]
      │
      │ (8) assets/auth-bar.js → /cdn-cgi/access/get-identity 호출
      │     → 응답 JSON 의 email 을 우측 상단에 표시
      ▼
[완료]
```

### 3-2. 두 번째 진입 이후

CF_Authorization 쿠키가 살아 있는 동안 (④ Session Duration 24h) 은 위 (2)~(6) 단계를 모두 건너뛰고 곧바로 (7) 로 진입한다 → 사용자 입장에서는 **즉시 대시보드 표시**.

### 3-3. SSO가 깨지는 대표 상황

| 상황 | 원인 | 대처 |
|---|---|---|
| Teams 데스크탑만 무한 로그인 루프 | Cookie SameSite ≠ None | ACCESS_CONSOLE_SETUP.md **④-2** 재확인 |
| 매번 Entra ID 로그인 화면이 뜸 | Teams 가 회사 계정으로 로그인되어 있지 않음 / 시크릿 브라우저 | 정상 (보안 동작) |
| 모바일에서만 차단 | iOS/Android Teams 의 일부 버전에서 third-party cookie 정책 | Teams 앱 업데이트 → 그래도 실패면 `*.cloudflareaccess.com` 을 `validDomains` 에 추가 |
| 로그아웃 후 재로그인 시 이전 계정으로 자동 로그인 | Teams 컨테이너 자체 세션 | Teams 의 "전체 로그아웃" 또는 디바이스의 회사 계정 분리 필요 (Access 책임 범위 밖) |

---

## 4. 운영 시 주의사항

### 4-1. URL 변경이 발생하면

대시보드 URL 또는 Cloudflare Access 도메인이 변경될 경우, **반드시 다음 5곳을 동시에 갱신**해야 한다.

| # | 위치 | 변경 대상 |
|---|---|---|
| 1 | `teams-app/manifest.json` | `developer.websiteUrl`, `staticTabs[].contentUrl`, `staticTabs[].websiteUrl`, `validDomains[]` |
| 2 | `index.html` | `<meta name="cf-access-team-domain">` |
| 3 | `_redirects` | `/logout` 대상 URL |
| 4 | Cloudflare Access | Application domain (④) + Entra ID 리디렉션 URI (②) |
| 5 | Teams 관리 센터 | 새 manifest zip 으로 앱 패키지 업데이트 |

`teams-app/manifest.json` 의 `version` 도 함께 올려야 (예: `1.0.3` → `1.0.4`) Teams 가 업데이트를 인식한다.

### 4-2. Teams 앱 업데이트 배포

1. `teams-app/` 폴더에서 `manifest.json`, `color.png`, `outline.png` 3개를 **zip 의 최상위 루트**에 위치하도록 압축. (폴더째 압축 금지)
2. Teams 관리 센터(`admin.teams.microsoft.com`) → **Teams 앱** → **앱 관리** → 기존 앱 검색 → **업데이트** → zip 업로드.
3. 검수 후 정책 할당(대상 사용자/그룹) → 1~2시간 내 클라이언트에 반영.

### 4-3. 미리보기 / 사이드 로드

운영 배포 전 본인 계정으로만 미리 확인하려면:
- Teams 데스크탑 → 좌측 **앱** → **앱 관리** → **+ 앱 업로드** → **나에게 업로드**.
- 사이드로드 권한이 막혀 있으면 IT에 **App setup policy** 의 "사용자 지정 앱 업로드 허용" 권한 요청.

### 4-4. 보안 검토 응답 준비

DX운영그룹 또는 IT보안팀이 다음을 질의할 가능성:

| 질의 | 답변 근거 |
|---|---|
| 대시보드 자체 로그인이 있나? | 없음. 인증은 Cloudflare Access + Entra ID 가 전적으로 담당. 앱 단 로그인 미구현. |
| URL 직접 접근 시 차단되나? | Access Policy 미매칭 사용자는 Cloudflare 단계에서 차단됨. (테스트 ⑥-1) |
| 외부(`@gmail.com` 등) 차단되나? | Entra ID 테넌트 외부 계정은 IdP 단계에서 인증 자체가 실패. |
| 쿠키는 안전한가? | CF_Authorization 은 Cloudflare 서명된 JWT 기반. SameSite=None; Secure; Domain 한정. HTTP-only 는 Teams 호환을 위해 해제(④-2). |
| 데이터는 어디 있나? | 현재 모든 데이터는 정적 JS (`data.js`, `photos.js`) 에 포함. 외부 DB/API 호출 없음. (SharePoint 전환 시 별도 검토) |

---

## 5. 관련 문서

- `docs/ACCESS_CONSOLE_SETUP.md` — Cloudflare Access + Entra ID 콘솔 설정 (선행 문서)
- `docs/FALLBACK_SHAREPOINT.md` — Access 적용이 어려운 경우의 대안 시나리오
- `README.md` / `DEPLOYMENT.md` — 빌드/배포 일반 절차
