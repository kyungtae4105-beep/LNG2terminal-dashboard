# 배포 가이드 — Cloudflare Pages + Cloudflare Access

> 📋 **목표**: 정적 대시보드를 Cloudflare Pages로 호스팅하고, Cloudflare Access로 이메일 화이트리스트 접근 제어를 적용합니다.
> **승인자**: `kyungtae@poscointl.com` 이 모든 접근 신청을 승인합니다.
> **저장소**: `https://github.com/kyungtae4105-beep/LNG2terminal-dashboard` (Private)

---

## 0. 한눈에 보기

```
[로컬 작업]
   git commit + push (main)
        │
        ▼
[GitHub Private Repo: kyungtae4105-beep/LNG2terminal-dashboard]
        │ webhook
        ▼
[Cloudflare Pages] ── 정적 서빙 (build cmd 없음, output dir = /)
        │
        ▼
[Cloudflare Access 게이트] ── 이메일 OTP + 화이트리스트
        │
        ▼
[승인된 사용자만 접근 가능]
```

소요 시간: 최초 설정 ~30분, 이후 데이터 갱신은 `git push` 1회로 1~2분.

---

## ✅ 1단계 — GitHub Private Repo 생성 & Push

### 1-1. GitHub Repo 준비
이미 `https://github.com/kyungtae4105-beep/LNG2terminal-dashboard` 가 생성되어 있습니다. 새로 만든다면:
1. https://github.com/new 접속
2. 입력값:
   - **Repository name**: `LNG2terminal-dashboard` (또는 원하는 이름)
   - **가시성**: **Private** (반드시 체크)
   - **Initialize repository**: 모두 체크 해제
3. **Create repository** 클릭

### 1-2. 로컬에서 push
```powershell
# 작업 폴더 이동 불필요 (CWD가 이미 대시보드 폴더)

# 원격 등록 (이미 등록되어 있으면 skip)
git remote add origin https://github.com/kyungtae4105-beep/LNG2terminal-dashboard.git

# 첫 push
git branch -M main
git push -u origin main
```

처음 push 시 GitHub 인증창이 뜹니다:
- **Windows**: Git Credential Manager가 브라우저로 OAuth 로그인을 안내
- 또는 **PAT(Personal Access Token)** 입력 — https://github.com/settings/tokens/new 에서 `repo` 권한으로 발급

### 1-3. `.gitignore` 권장 항목
```
ppt_extract/
*.pptx
.DS_Store
Thumbs.db
*.tmp
.env
```

원본 PPT가 큰 이진 파일이고 DRM이 걸려 있어 push 대상이 아닙니다.

---

## ✅ 2단계 — Cloudflare Pages 배포

### 2-1. Cloudflare 계정
1. https://dash.cloudflare.com/sign-up 에서 계정 생성 (또는 로그인)
2. 무료 플랜으로 충분
   - Pages: 월 500 빌드 무료
   - Access: 50 사용자까지 무료

### 2-2. Pages 프로젝트 생성
1. Cloudflare 대시보드 → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**
2. GitHub 연동 인증 (처음이면 OAuth 진행)
3. `LNG2terminal-dashboard` repo 선택 → **Begin setup**
4. **Build settings**:
   - Project name: `lng-dashboard` (자유)
   - Production branch: `main`
   - **Framework preset**: `None`
   - **Build command**: 비워둠
   - **Build output directory**: `/` (루트)
5. **Save and Deploy** 클릭

1~2분 후 `https://lng-dashboard-xxxx.pages.dev` 형태의 URL이 발급됩니다.
> ⚠️ 이 시점에는 누구나 볼 수 있습니다. 다음 단계에서 잠급니다.

### 2-3. `_headers` 검증
저장소 루트의 `_headers` 파일이 자동으로 인식되어 다음 정책이 적용되는지 확인:
```
/photos/*       → Cache-Control: public, max-age=31536000, immutable
/*.js           → Cache-Control: public, max-age=300
/*.html         → Cache-Control: public, max-age=60
                  X-Frame-Options: DENY
                  X-Content-Type-Options: nosniff
                  Referrer-Policy: same-origin
```

DevTools Network 탭에서 헤더 확인 가능.

---

## ✅ 3단계 — Cloudflare Access (이메일 화이트리스트)

### 3-1. Zero Trust 활성화
1. Cloudflare 대시보드 → 우측 사이드바 **Zero Trust** 클릭
2. 처음이면 Team name 입력 (예: `posco-tf`) → 무료 플랜 선택 → 결제 정보 등록
   (무료 플랜이지만 카드 등록 필요)

### 3-2. 인증 방법 등록 — Email OTP
1. Zero Trust 대시보드 → **Settings** → **Authentication** → **Login methods** → **Add new**
2. **One-time PIN** 선택 → **Save**

이로써 사용자는 이메일 입력 → 6자리 OTP 메일 수신 → 로그인 가능.

### 3-3. Access Application 등록
1. Zero Trust 대시보드 → **Access** → **Applications** → **Add an application**
2. **Self-hosted** 선택
3. **Application Configuration**:
   - Application name: `LNG Dashboard`
   - Session Duration: `24 hours`
   - Application domain: `lng-dashboard-xxxx.pages.dev` (2-2에서 발급된 도메인)
4. **Next**

### 3-4. Access Policy — 이메일 화이트리스트
1. **Add a policy**:
   - Policy name: `Approved users`
   - Action: **Allow**
   - **Include** → **Emails** → 승인 이메일 목록 입력
     - 예: `kyungtae@poscointl.com`, `colleague1@poscointl.com`, …
2. **Next** → **Add application**

이제 누군가 대시보드 URL로 접근하면:
1. Cloudflare 로그인 페이지가 뜸
2. 이메일 입력 → OTP 코드 발송 (`noreply@notify.cloudflare.com`)
3. 화이트리스트 일치 시 → OTP 입력 후 24시간 세션
4. 화이트리스트 외 → "권한 없음"

### 3-5. 신청자 추가 (운영)
`kyungtae@poscointl.com` 으로 신청 메일을 받으면:
1. Zero Trust → **Access** → **Applications** → `LNG Dashboard` → **Edit**
2. Policy → **Approved users** → **Edit**
3. **Include** → **Emails** 칸에 신청자 이메일 추가
4. **Save** — 즉시 적용

> 💡 **무료 플랜은 50 활성 사용자(Seat) 제한**. 그 이상은 사용자당 $7/월. 처음에는 무료로 시작 후 필요 시 업그레이드.

---

## ✅ 4단계 — 운영 워크플로우

### 4-1. 월간 데이터 갱신
```powershell
# (선택) UTF-8 인코딩 보장
$env:PYTHONIOENCODING="utf-8"

# 데이터/사진 변경 후
git add data.js photos.js photos/
git commit -m "월별 데이터 갱신 (YYYY-MM)"
git push origin main
# → Cloudflare Pages가 1~2분 내 자동 재배포
```

### 4-2. 사용자 관리

| 상황 | 조치 |
|---|---|
| 신규 신청 메일 | Zero Trust → Access → Applications → 정책 편집 → 이메일 추가 |
| 권한 회수 | 정책에서 이메일 삭제 |
| 누가 언제 로그인했는지 확인 | Zero Trust → Logs → Access |

### 4-3. 도메인 변경 (선택)
`*.pages.dev` 대신 자체 도메인을 쓰려면:
1. Cloudflare에 도메인 등록 (예: `lng.posco-international.com`)
2. Pages 프로젝트 → **Custom domains** 에서 도메인 추가
3. Access Application의 도메인도 새 도메인으로 변경
4. DNS Proxied(주황색 구름) ON 유지

### 4-4. 롤백
1. Cloudflare Pages → 프로젝트 → **Deployments** 탭
2. 이전 성공 배포 → **... 메뉴 → Rollback to this deployment**
3. 라이브 도메인이 즉시 해당 빌드로 전환

---

## 🚨 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `git push` 시 인증 실패 | PAT 발급 필요. https://github.com/settings/tokens/new → `repo` 체크 → 비밀번호 자리에 입력 |
| Cloudflare Pages 빌드 실패 | Build command 비어 있는지, output dir이 `/` 인지 확인 |
| Access 게이트가 안 뜸 | Application의 도메인이 정확한지 확인. `*.pages.dev` 도메인은 자동으로 `cloudflare.com` 으로 보호됨 |
| OTP 메일이 안 옴 | 스팸함 확인. Cloudflare 발신: `noreply@notify.cloudflare.com` |
| OneDrive 동기화로 인해 push 실패 | `.git` 폴더가 손상되면 → 프로젝트를 OneDrive 외부 위치(`C:\Users\<user>\projects\lng-dashboard\`)로 옮긴 뒤 다시 진행 |
| 한글 폴더명(`01월`/`02월`) 문제 | OS는 정상 처리. git 환경 변수 `core.quotepath=false` 권장 |
| Chart.js / Pretendard 차단(사내망) | jsDelivr · googleapis 도메인 화이트리스트 신청 또는 self-host 검토 |
| `_headers` 가 적용되지 않음 | 파일이 저장소 **루트**에 있어야 함. 서브폴더 안에 두면 무시됨 |
| 누락월(`null`) 차트가 깨짐 | Chart.js의 `spanGaps: false` 옵션 확인 |
| 사진 401/403 | Cloudflare Access 정책이 `/photos/*` 도 보호하는지 확인. 보통 자동 적용 |

---

## 📞 운영 연락

- **시스템 관리자**: kyungtae@poscointl.com
- **저장소**: https://github.com/kyungtae4105-beep/LNG2terminal-dashboard
- **이슈 등록**: GitHub Issues 또는 위 이메일

---

© 2026 POSCO INTERNATIONAL — 에너지건설 TF
