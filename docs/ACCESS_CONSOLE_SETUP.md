# Cloudflare Access + Microsoft Entra ID 콘솔 설정 가이드

> **대상 독자**: 박경태 대리(에너지건설TF) 및 DX기획·운영그룹 담당자
> **목적**: 광양 제2 LNG터미널 Dashboard(`https://energytf-dashboard.pages.dev/`)에 회사 계정 기반 접근 통제를 적용하기 위한 **콘솔 설정** 절차를 비개발자가 따라할 수 있도록 단계별로 정리.
> **결과**: URL을 알아도 회사 계정으로 인증되지 않으면 대시보드가 열리지 않으며, Microsoft Teams 탭에서도 동일한 인증이 자동 적용됨.

---

## 0. 전체 흐름 한 장 요약

```
[사용자]
   │  ① URL 접속 (https://energytf-dashboard.pages.dev/)
   ▼
[Cloudflare Access]  ──── 미인증이면 차단 ───→ Entra ID 로그인 화면으로 리다이렉트
   │  ② 회사 계정으로 로그인
   ▼
[Microsoft Entra ID]  ─── 허용된 사용자/그룹 검증
   │  ③ 인증 토큰 발급
   ▼
[Cloudflare Access]  ─── Policy 통과 시 CF_Authorization 쿠키 발급
   │
   ▼
[대시보드]  ─── 정상 표시 (우측 상단에 "로그인: {email}" 표시)
```

> Teams 탭에서 열어도 동일 흐름. iframe 안에서 Access 가 쿠키를 인식하고 그대로 통과시킴.

---

## 1. 시작 전 준비물

| 항목 | 비고 |
|---|---|
| Cloudflare 계정 (관리자 권한) | 미보유 시 신규 가입 (이메일 + 카드 1회 등록) |
| Microsoft Entra ID 관리자 권한 | "앱 등록" 가능 권한 (Application Administrator 이상) |
| 회사 IT보안팀 사전 협의 | Entra ID 신규 앱 등록 / 클라이언트 시크릿 발급 |
| 파일럿 사용자 이메일 리스트 | 박경태 대리 + 에너지건설TF 담당자 + DX기획/운영그룹 테스트 담당자 (3~5명) |
| 운영 도메인 확정 | `energytf-dashboard.pages.dev` (이미 운영 중) |

---

## ① Cloudflare Zero Trust 팀 생성

**위치**: Cloudflare 대시보드 → 좌측 메뉴 **Zero Trust**

![](TODO: Cloudflare Zero Trust 시작 화면 스크린샷)

1. 처음 진입 시 팀 이름 입력 화면이 표시됨.
2. **Team name**: `energytf` (예시 — 변경 시 본 문서 전체와 `_redirects` / `index.html` 의 `cf-access-team-domain` 메타도 함께 수정 필요).
3. **Plan 선택**: **Free** (사용자 50명까지 무료).
   - ⚠️ Free 플랜도 최초 1회 카드 등록이 필요함 (실 청구는 없음).
4. 생성 완료 시 **발급 도메인**이 표시됨:
   ```
   https://energytf.cloudflareaccess.com
   ```
   이 도메인은 이후 ② Entra ID 앱 등록의 **리디렉션 URI** 및 본 대시보드의 **로그아웃 URL**에 사용된다.

| 메모할 값 | 위치 |
|---|---|
| Team name (slug) | `energytf` |
| 발급 도메인 | `https://energytf.cloudflareaccess.com` |

---

## ② Microsoft Entra ID 앱 등록

**위치**: [portal.azure.com](https://portal.azure.com) → **Microsoft Entra ID** → **앱 등록** → **+ 새 등록**

![](TODO: Entra ID 앱 등록 - 새 등록 화면 스크린샷)

### 2-1. 기본 정보 입력
- **이름**: `Cloudflare Access - EnergyTF Dashboard`
- **지원되는 계정 유형**: **단일 테넌트** (이 디렉터리에만 있는 계정)
- **리디렉션 URI(웹)**:
  ```
  https://energytf.cloudflareaccess.com/cdn-cgi/access/callback
  ```
  ⚠️ ①에서 발급된 도메인 + `/cdn-cgi/access/callback` 형식. 오타 한 글자라도 다르면 로그인이 실패함.

### 2-2. 클라이언트 시크릿 발급
좌측 메뉴 → **인증서 및 비밀** → **+ 새 클라이언트 비밀**

![](TODO: 클라이언트 시크릿 발급 화면 스크린샷)

- **설명**: `Cloudflare Access — created YYYY-MM-DD`
- **만료**: **24개월** 권장
- ⚠️ **Value(값) 컬럼은 발급 직후에만 보임.** 페이지를 벗어나면 다시 볼 수 없으므로 **즉시 복사**해 둘 것.

### 2-3. API 권한 부여
좌측 메뉴 → **API 권한** → **+ 권한 추가** → **Microsoft Graph** → **위임된 권한**

다음 권한 모두 추가:

| 권한 | 용도 |
|---|---|
| `email` | 이메일 주소 받기 |
| `openid` | OIDC 인증 |
| `profile` | 기본 프로필 |
| `offline_access` | 토큰 재발급 |
| `User.Read` | 본인 정보 조회 |
| `GroupMember.Read.All` | (보안그룹 기반 정책 사용 시) 그룹 멤버십 조회 |

추가 후 반드시 **[테넌트]에 대한 관리자 동의 부여** 버튼 클릭.

![](TODO: API 권한 부여 - 관리자 동의 완료 화면 스크린샷)

### 2-4. 필수 메모
다음 3개 값을 안전한 곳에 별도로 보관 (③에서 사용):

| 값 | 위치 |
|---|---|
| **Application(Client) ID** | 앱 등록 → 개요 |
| **Directory(Tenant) ID** | 앱 등록 → 개요 |
| **Client Secret Value** | 2-2 단계에서 발급된 값 (재조회 불가) |

> ⚠️ **IT보안팀 승인 필요 가능성**: 사내 정책에 따라 "외부 SaaS(Cloudflare)를 IdP에 연결하는 신규 앱 등록"이 보안 검토 대상이 될 수 있음. 진행 전 보안팀에 사전 협의 권장.

---

## ③ Cloudflare에 Entra ID를 IdP로 등록

**위치**: Zero Trust 대시보드 → **Settings** → **Authentication** → **Login methods** → **+ Add new**

![](TODO: Zero Trust Login methods 화면 스크린샷)

1. **Provider** 선택: **Azure AD** (Microsoft Entra ID의 구 명칭이 화면에 표시됨).
2. 입력 필드:

| 필드 | 값 |
|---|---|
| Name | `Entra ID - EnergyTF` (구분용) |
| App ID | ②에서 메모한 Application(Client) ID |
| Application secret | ②에서 메모한 Client Secret Value |
| Directory ID | ②에서 메모한 Tenant ID |
| Support groups | ✅ 체크 (보안그룹 정책 사용 시 필수) |

3. 저장 후 **Test** 버튼 클릭 → 본인 회사 계정으로 로그인 → "Your connection works!" 메시지가 떠야 정상.

![](TODO: Test 버튼 정상 응답 화면 스크린샷)

> Test에 실패한다면 99% 다음 두 가지 중 하나:
> - 리디렉션 URI 오타 (Entra ID 측 ②와 정확히 일치하는지)
> - Client Secret 값 오타 (다시 발급 후 재입력)

---

## ④ Access Application 생성

**위치**: Zero Trust → **Access** → **Applications** → **+ Add an application** → **Self-hosted**

![](TODO: Access Application 생성 - Self-hosted 화면 스크린샷)

### 4-1. 기본 설정
| 필드 | 값 |
|---|---|
| Application name | `EnergyTF Dashboard` |
| Session Duration | **24 hours** (현업 사용자 편의성 ↔ 보안 균형) |
| Application domain | `energytf-dashboard.pages.dev` |
| Path | (비움 — 전체 사이트 보호) |
| Identity providers | ③에서 등록한 `Entra ID - EnergyTF` 만 체크 |

### 4-2. ⚠️ Teams 임베드용 필수 설정 (절대 빠뜨리지 말 것)
**Application 설정 화면 하단** 또는 **Advanced settings** 내부:

| 설정 | 값 | 누락 시 증상 |
|---|---|---|
| **Cookie SameSite** | **None** | Teams iframe 안에서 쿠키 미인식 → 무한 로그인 루프 |
| **Always Use HTTPS** | **On** | SameSite=None 은 Secure 쿠키 강제 → HTTPS 필수 |
| **HTTP Only** | **해제** | (선택) 일부 환경에서 Teams JS SDK 호환을 위해 해제 권장 |

> ⚠️ **이 3개 설정을 누락하면 데스크탑 Teams 에서 대시보드 탭이 열리지 않고 무한 로그인 루프가 발생함.** 본 문서에서 가장 자주 빠뜨리는 함정이니 반드시 확인.

![](TODO: Cookie SameSite=None / Always Use HTTPS=On 설정 스크린샷)

---

## ⑤ Access Policy 작성

**위치**: ④에서 생성한 Application → **Policies** 탭 → **+ Add a policy**

| 필드 | 값 |
|---|---|
| Policy name | `Allow - EnergyTF Pilot` (단계별 변경) |
| Action | **Allow** |
| Session duration | (Application 설정 상속) |

### Include 규칙 — 3가지 옵션 중 선택

#### 옵션 A. **Emails 개별** (초기 파일럿 — 권장 시작점)
- Selector: **Emails**
- Value:
  ```
  parkkt@회사도메인.com         # 박경태 대리 (에너지건설TF)
  energytf.member1@회사도메인.com
  energytf.member2@회사도메인.com
  dx-test.member1@회사도메인.com  # DX기획·운영그룹 테스트 담당자
  dx-test.member2@회사도메인.com
  ```
- 장점: 빠르게 시작 / 통제 명확
- 단점: 인원 변동 시 수동 관리

#### 옵션 B. **Emails ending in @회사도메인.com** (전사 확대)
- Selector: **Emails ending in**
- Value: `@회사도메인.com`
- 장점: 추가 작업 없이 전사 적용
- 단점: 너무 광범위 (부적절한 사용자도 접근 가능)

#### 옵션 C. **Azure AD groups** ⭐ 권장 (확대 운영)
- Selector: **Azure AD groups**
- Value: `EnergyTF-Dashboard-Users` (Entra ID 측에서 보안그룹 사전 생성 필요)
- 장점: 인사이동을 그룹 멤버십으로 일원화 관리
- 단점: 그룹 생성/멤버 관리 권한자 협조 필요

> **운영 권장 순서**: 옵션 A (파일럿 3~5명) → 안정 확인 → 옵션 C (그룹 기반 확대).

> **Block 정책 불필요**: Access 는 "Allow 에 매칭되지 않으면 자동 차단" 이므로 별도 Block 정책을 추가하지 않는다. 단, 특정 사용자만 차단해야 할 경우(예: 퇴사자 즉시 차단)에만 Deny 정책을 **상단**에 배치.

![](TODO: Policy 작성 - 옵션 C 그룹 선택 화면 스크린샷)

---

## ⑥ 동작 테스트 체크리스트

### 6-1. 직접 URL 접근 테스트

| # | 시나리오 | 기대 결과 | 확인 |
|---|---|---|---|
| 1 | 시크릿 브라우저로 `https://energytf-dashboard.pages.dev/` 접속 | Entra ID 로그인 화면으로 리다이렉트 | ☐ |
| 2 | 허용 계정 (예: 박경태 대리) 로 로그인 | 대시보드 정상 표시 + 우측 상단 "로그인: parkkt@..." 표시 | ☐ |
| 3 | 미허용 회사 계정으로 로그인 | Cloudflare **Access denied** 페이지 (회사 도메인은 통과되지만 ⑤ Allow 정책에 미매칭) | ☐ |
| 4 | 외부 이메일 (예: `@gmail.com`) 로 로그인 시도 | Entra ID 인증 자체가 실패 (테넌트 외부 계정) | ☐ |

### 6-2. Teams 탭 임베드 테스트

| # | 환경 | 기대 결과 | 확인 |
|---|---|---|---|
| 1 | **Teams 데스크탑** (Windows/macOS) | 탭 진입 시 자동 인증되어 대시보드 표시 | ☐ |
| 2 | **Teams 웹** (`teams.microsoft.com`) | 동일 | ☐ |
| 3 | **Teams 모바일** (iOS/Android) | 동일 (최초 1회 Entra ID 로그인 후 SSO 유지) | ☐ |

### 6-3. 실패 시 점검 포인트

| 증상 | 점검 위치 |
|---|---|
| Teams 데스크탑에서만 무한 로그인 루프 | **④의 Cookie SameSite = None** 누락 확인 |
| 브라우저는 OK인데 Teams iframe 차단 | 코드 측 `_headers` 의 **CSP frame-ancestors** 에 `teams.microsoft.com` / `*.office.com` 포함 여부 |
| `Access denied` 가 떠야 할 사용자도 통과됨 | ⑤ Policy 의 Include 규칙 (특히 옵션 B `ending in @회사도메인.com` 범위 점검) |
| 위 모두 OK 인데 여전히 실패 | **`docs/FALLBACK_SHAREPOINT.md`** 참조 — SharePoint/SPFx 전환 검토 (메일 3단계) |

---

## 운영 단계 체크리스트 (담당자 / 소요시간)

| 단계 | 담당 | 소요시간 |
|---|---|---|
| ① Zero Trust 팀 생성 | DX운영그룹 (Cloudflare 계정 보유자) | 10분 |
| ② Entra ID 앱 등록 (+ 보안팀 사전 협의) | IT보안팀 협조 + DX운영그룹 | 1~2일 (보안 검토 포함) |
| ③ IdP 연계 (Cloudflare ← Entra ID) | DX운영그룹 | 15분 |
| ④ Access Application 생성 | DX운영그룹 | 10분 |
| ⑤ Access Policy 작성 (옵션 A 파일럿) | DX운영그룹 + 박경태 대리 (대상자 명단 제공) | 20분 |
| ⑥ 동작 테스트 (직접 URL 4종 + Teams 3종) | 박경태 대리 + 파일럿 사용자 | 1~2시간 |
| (추가) 옵션 C 그룹 정책 확대 적용 | IT인프라 (그룹 생성) + DX운영그룹 | 1~2일 |

---

## 보안 운영 팁

- **Client Secret 만료일 캘린더 등록**: ②-2 에서 24개월로 발급한 시크릿은 만료 30일 전 알림을 사내 일정에 미리 등록 (만료 시 무중단 갱신은 Cloudflare 측 시크릿 교체로 처리).
- **감사로그 활성화**: Zero Trust → **Logs** → **Access** 에서 로그인/거부 이력을 정기 확인. CSV 내보내기로 분기 1회 보안팀 공유 권장.
- **Service Tokens**: 추후 외부 시스템이 본 대시보드 또는 API를 자동화로 호출할 일이 생기면 Access → **Service Auth** → **Service Tokens** 를 사용. **사용자 정책과 분리**.
- **정책 우선순위**: Deny 정책은 반드시 **목록 상단**에 배치. Access 는 위→아래 순서로 평가 후 첫 매칭에서 확정한다.
- **세션 만료**: ④의 Session Duration 24h 는 노트북 분실 등을 고려한 트레이드오프. 보안 강화가 필요하면 8h 또는 4h 로 단축.
- **정기 점검(분기 1회 권장)**:
  - 파일럿 → 옵션 C 그룹 이관 진행 현황
  - 퇴사자/조직변경자 그룹 자동 제거 확인
  - Entra ID 앱 권한 변동 여부

---

## 부록 — 자주 묻는 질문

**Q. Free 플랜으로 충분한가요?**
A. 사용자 50명 이내라면 충분. 초과 시 Pay-as-you-go (사용자 1명당 약 $3/월 수준, 변동 가능).

**Q. 회사 IT보안팀이 Entra ID 앱 등록을 거부하면?**
A. `docs/FALLBACK_SHAREPOINT.md` 의 SharePoint/SPFx 전환 시나리오를 검토. M365 정책 정합성이 가장 높은 대안.

**Q. 도메인을 운영 도중에 바꾸려면?**
A. 다음 3곳을 동시에 갱신해야 함:
1. `_redirects` 의 `/logout` 라인
2. `index.html` 의 `<meta name="cf-access-team-domain">`
3. Entra ID 앱 등록의 **리디렉션 URI**
