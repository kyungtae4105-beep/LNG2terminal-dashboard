/* ============================================================
 * AUTH BAR — Cloudflare Access 사용자 표시 / 로그아웃
 * ------------------------------------------------------------
 * 동작:
 *   1) Cloudflare Access 가 앞단에서 인증을 처리한다.
 *   2) 본 스크립트는 인증된 사용자 이메일을 화면 우측 상단에
 *      "로그인: {email}  |  로그아웃" 형태로 표시한다.
 *   3) 이메일 조회 우선순위:
 *        a. <meta name="cf-access-debug-email"> (로컬 개발용)
 *        b. /cdn-cgi/access/get-identity (Cloudflare Access 표준 엔드포인트)
 *           - 헤더 Cf-Access-Authenticated-User-Email 는 서버측에서만
 *             신뢰 가능. 클라이언트에서는 본 엔드포인트의 JSON을 사용.
 *   4) 이메일을 얻지 못하면 "로컬 개발자 모드 — 인증정보 없음" 배지 표시
 *      (운영 빌드/도메인에서는 노출되지 않도록 호스트네임 기반 분기).
 *
 * 보안 메모:
 *   - 본 스크립트는 인증을 "검증"하지 않는다. 검증은 Access(앞단)와
 *     Pages Functions(필요 시) 에서만 수행.
 *   - 로그아웃 URL 의 팀 도메인은 <meta name="cf-access-team-domain">
 *     로부터 읽는다. 하드코딩 금지.
 *   - 쿠키(CF_Authorization)는 Teams iframe 호환을 위해 Access 설정 측에서
 *     SameSite=None; Secure 로 발급되어야 한다. 본 스크립트는 쿠키를
 *     직접 다루지 않는다.
 * ============================================================ */

(function () {
  'use strict';

  // ----- 유틸 ---------------------------------------------------
  function $meta(name) {
    const el = document.querySelector('meta[name="' + name + '"]');
    return el ? (el.getAttribute('content') || '').trim() : '';
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function isProductionHost() {
    // Cloudflare Pages 운영 / *.pages.dev / 회사 도메인을 production 으로 간주.
    // localhost / 127.0.0.1 / file:// 은 로컬 개발로 간주.
    const h = (location.hostname || '').toLowerCase();
    if (!h) return false;
    if (h === 'localhost' || h === '127.0.0.1' || h === '::1') return false;
    return true;
  }

  // ----- 이메일 조회 -------------------------------------------
  function fetchIdentityEmail() {
    // 1) 로컬 디버그용 메타 우선
    const debugEmail = $meta('cf-access-debug-email');
    if (debugEmail) return Promise.resolve(debugEmail);

    // 2) Cloudflare Access 표준 엔드포인트
    //    - Access 통과 시 200 + JSON({ email: "...", ... })
    //    - 미통과/로컬: 일반적으로 4xx 또는 네트워크 오류
    return fetch('/cdn-cgi/access/get-identity', {
      credentials: 'include',
      cache: 'no-store',
      headers: { 'Accept': 'application/json' },
    })
      .then(function (res) {
        if (!res.ok) return null;
        return res.json().catch(function () { return null; });
      })
      .then(function (json) {
        if (!json) return '';
        return (json.email || json.user_email || json.name || '').toString().trim();
      })
      .catch(function () { return ''; });
  }

  // ----- 로그아웃 URL 조립 -------------------------------------
  function buildLogoutUrl() {
    const team = $meta('cf-access-team-domain');
    if (!team) return ''; // 도메인이 없으면 로그아웃 불가 (로컬 등)
    // 예: https://energytf.cloudflareaccess.com/cdn-cgi/access/logout
    return 'https://' + team + '.cloudflareaccess.com/cdn-cgi/access/logout';
  }

  // ----- 렌더링 -------------------------------------------------
  function render(email) {
    const mount = document.getElementById('auth-bar');
    if (!mount) return;

    const logoutUrl = buildLogoutUrl();
    const isProd = isProductionHost();

    if (email) {
      const logoutHtml = logoutUrl
        ? '<a class="auth-bar__logout" href="' + escapeHtml(logoutUrl) + '">로그아웃</a>'
        : '';
      mount.innerHTML =
        '<span class="auth-bar__user" title="' + escapeHtml(email) + '">' +
        '로그인: <b>' + escapeHtml(email) + '</b>' +
        '</span>' +
        (logoutHtml ? '<span class="auth-bar__sep">|</span>' + logoutHtml : '');
      mount.dataset.state = 'authed';
      return;
    }

    // 이메일 없음
    if (!isProd) {
      // 로컬 개발 환경에서만 배지 노출
      mount.innerHTML = '<span class="auth-bar__dev">로컬 개발자 모드 — 인증정보 없음</span>';
      mount.dataset.state = 'dev';
    } else {
      // 운영 도메인에서 이메일이 비어 있다면 Access 설정 이상.
      // 사용자 혼란을 막기 위해 빈 상태로 유지 (콘솔 경고만).
      mount.innerHTML = '';
      mount.dataset.state = 'empty';
      // eslint-disable-next-line no-console
      console.warn('[auth-bar] Access identity 를 조회하지 못했습니다. /cdn-cgi/access/get-identity 응답을 확인하세요.');
    }
  }

  // ----- 부팅 ---------------------------------------------------
  function boot() {
    if (!document.getElementById('auth-bar')) return;
    fetchIdentityEmail().then(render);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
