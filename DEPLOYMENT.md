# 배포 가이드 — Cloudflare Pages + Cloudflare Access

> 📋 **목표**: 정적 대시보드를 Cloudflare Pages로 호스팅하고, Cloudflare Access로 이메일 화이트리스트 접근 제어를 적용합니다. **kyungtae@poscointl.com** 이 모든 접근 신청을 승인합니다.

---

## ✅ 1단계 — GitHub Private Repo 생성 & Push

### 1-1. GitHub에서 Private Repo 생성

1. https://github.com/new 접속
2. 다음과 같이 입력:
   - **Repository name**: `lng-dashboard` (또는 원하는 이름)
   - **Description**: `광양 제2 LNG터미널 증설공사 주요 지표 Dashboard`
   - **가시성**: **Private** (반드시 체크)
   - **Initialize repository**: 모두 체크 해제 (README/.gitignore/license 체크하지 말 것 — 이미 로컬에 있음)
3. **Create repository** 클릭

### 1-2. 로컬에서 push

생성된 repo 페이지의 URL을 복사한 뒤, 터미널에서:

```bash
cd "C:/Users/kyungtae/OneDrive - POSCO INTERNATIONAL/바탕 화면/대시보드"

# 첫 push (GitHub에서 안내한 명령 그대로)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/lng-dashboard.git
git branch -M main
git push -u origin main
```

처음 push 시 GitHub 인증창이 뜹니다:
- Windows: Git Credential Manager가 브라우저로 OAuth 로그인을 안내함
- 또는 Personal Access Token(PAT) 입력 — https://github.com/settings/tokens/new 에서 `repo` 권한으로 발급

---

## ✅ 2단계 — Cloudflare Pages 배포

### 2-1. Cloudflare 계정 준비

1. https://dash.cloudflare.com/sign-up 에서 계정 생성 (이미 있으면 로그인)
2. 무료 플랜으로 충분 (Pages는 월 500 빌드 무료, Access는 50 사용자까지 무료)

### 2-2. Pages 프로젝트 생성

1. Cloudflare 대시보드 → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**
2. GitHub 연동 인증 (처음이면 OAuth 진행)
3. 방금 만든 `lng-dashboard` repo 선택 → **Begin setup**
4. **Build settings**:
   - Project name: `lng-dashboard` (그대로)
   - Production branch: `main`
   - **Framework preset**: `None`
   - **Build command**: 비워둠
   - **Build output directory**: `/` (루트 그대로)
5. **Save and Deploy** 클릭

1~2분 후 `https://lng-dashboard-xxxx.pages.dev` 형태의 URL이 발급됩니다. 이 URL로 접근하면 — 아직은 누구나 볼 수 있습니다. 다음 단계에서 잠급니다.

---

## ✅ 3단계 — Cloudflare Access (이메일 화이트리스트)

### 3-1. Zero Trust 활성화

1. Cloudflare 대시보드 → 우측 사이드바 **Zero Trust** 클릭
2. 처음 활성화하는 경우 Team name 입력 (예: `posco-tf`) → 무료 플랜 선택 → 결제 정보 입력 (무료 플랜이지만 카드 등록 필요)

### 3-2. 인증 방법 등록 — Email OTP

1. Zero Trust 대시보드 → **Settings** → **Authentication** → **Login methods** → **Add new**
2. **One-time PIN** 선택 → **Save**

이로써 사용자는 자신의 이메일 주소를 입력하면 → 메일로 6자리 OTP 코드를 받아 로그인할 수 있게 됩니다.

### 3-3. Access Application 등록

1. Zero Trust 대시보드 → **Access** → **Applications** → **Add an application**
2. **Self-hosted** 선택
3. **Application Configuration**:
   - Application name: `LNG Dashboard`
   - Session Duration: `24 hours` (적절히 선택)
   - Application domain: `lng-dashboard-xxxx.pages.dev` (2-2에서 발급된 도메인)
4. **Next**

### 3-4. Access Policy — 이메일 화이트리스트

1. **Add a policy**:
   - Policy name: `Approved users`
   - Action: **Allow**
   - **Include** → **Emails** → 승인할 이메일 주소들을 줄바꿈/콤마로 입력
     - 예: `kyungtae@poscointl.com`, `colleague1@poscointl.com`, ...
2. **Next** → **Add application**

이제 누군가 대시보드 URL로 접근하면:
1. Cloudflare 로그인 페이지가 뜸
2. 이메일 입력 → OTP 코드 발송
3. 화이트리스트에 있으면 → OTP 입력 후 대시보드 로딩
4. 화이트리스트에 없으면 → "권한 없음" 화면 표시

### 3-5. 신청자 추가 (운영)

`kyungtae@poscointl.com` 으로 신청 메일을 받으면:

1. Zero Trust → **Access** → **Applications** → `LNG Dashboard` → **Edit**
2. Policy → **Approved users** → **Edit**
3. **Include** → **Emails** 칸에 신청자 이메일 추가
4. **Save** — 즉시 적용됨

> 💡 **주의**: 무료 플랜은 50 활성 사용자(Seat) 제한. 그 이상은 사용자당 $7/월. 처음에는 무료 플랜으로 시작 후 필요 시 업그레이드 권장.

---

## ✅ 4단계 — 운영 팁

### 데이터 갱신 워크플로우

```bash
# 데이터/사진 변경 후
git add .
git commit -m "월별 데이터 갱신 (4월)"
git push

# Cloudflare Pages가 자동으로 재배포 (1-2분)
```

### 사용자 관리

| 상황 | 조치 |
|---|---|
| 신규 신청 메일 | Cloudflare Zero Trust → Access → Applications → 정책 편집 → 이메일 추가 |
| 권한 회수 | 정책에서 이메일 삭제 |
| 누가 언제 로그인했는지 확인 | Zero Trust → Logs → Access |

### 도메인 변경 (선택)

`*.pages.dev` 대신 자체 도메인을 쓰려면:
1. Cloudflare에 도메인 등록
2. Pages 프로젝트 → **Custom domains** 에서 도메인 추가
3. Access Application의 도메인도 새 도메인으로 변경

---

## 🚨 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `git push` 시 인증 실패 | Personal Access Token 발급 필요. https://github.com/settings/tokens/new → `repo` 체크 → 토큰을 비밀번호 자리에 입력 |
| Cloudflare Pages 빌드 실패 | Build command 비어 있는지, output dir이 `/` 인지 확인 |
| Access 게이트가 안 뜸 | Application의 도메인이 정확한지 확인. `*.pages.dev` 도메인은 자동으로 cloudflare.com 으로 보호됨 |
| OTP 메일이 안 옴 | 스팸함 확인. Cloudflare는 `noreply@notify.cloudflare.com` 에서 발송 |
| OneDrive 동기화로 인해 push 실패 | `.git` 폴더가 손상되면 → 프로젝트를 OneDrive 외부 위치(`C:\Users\kyungtae\projects\lng-dashboard\`)로 옮긴 뒤 다시 진행 |

---

© 2026 POSCO INTERNATIONAL — 에너지건설 TF
