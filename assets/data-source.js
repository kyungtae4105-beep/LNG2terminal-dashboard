/* ============================================================
 * DATA_SOURCE — 데이터 어댑터 (Adapter Pattern)
 * ------------------------------------------------------------
 * 목적:
 *   index.html / 차트 코드가 직접 window.DASHBOARD_DATA,
 *   window.PHOTOS_DATA 를 참조하지 않고 본 어댑터를 통해서만
 *   읽도록 격리한다.
 *
 *   현재 구현은 정적 JS 전역(data.js, photos.js)에 위임만 한다.
 *   추후 SharePoint List / 문서 라이브러리 / Graph API 어댑터로
 *   교체할 때 본 파일만 수정하면 호출부는 변경 없이 동작한다.
 *
 * 사용:
 *   const kpi    = DATA_SOURCE.getKPI();
 *   const photos = DATA_SOURCE.getPhotos();
 *   const month  = DATA_SOURCE.getReferenceMonth();
 *
 * 주의:
 *   - 본 파일은 data.js / photos.js 이후에 로드되어야 한다.
 *   - 비동기 어댑터(SharePoint 등)로 교체될 가능성을 고려하여,
 *     호출부는 await 가능 형태(Promise.resolve 래핑) 도입을 권장.
 * ============================================================ */

(function (global) {
  'use strict';

  // ----- 내부 헬퍼 ---------------------------------------------
  function _kpiRoot() {
    // TODO(SharePoint): KPI 데이터 → SharePoint List 어댑터로 교체
    //   예) GET /sites/{siteId}/lists/{listId}/items?expand=fields
    //       권한: Sites.Read.All (위임) 또는 Sites.Selected
    return global.DASHBOARD_DATA || {};
  }

  function _photosRoot() {
    // TODO(SharePoint): 작업사진 → SharePoint 문서 라이브러리 어댑터로 교체
    //   예) GET /sites/{siteId}/drives/{driveId}/root/children
    //       권한: Files.Read.All (위임)
    return global.PHOTOS_DATA || {};
  }

  // ----- 공개 API ----------------------------------------------
  const DATA_SOURCE = {
    /** KPI 루트 객체 반환 (동기 — 정적 데이터) */
    getKPI: function () {
      return _kpiRoot();
    },

    /** 사진 루트 객체 반환 (동기 — 정적 데이터) */
    getPhotos: function () {
      return _photosRoot();
    },

    /** 기준월 문자열 (예: "2026.03") */
    getReferenceMonth: function () {
      const d = _kpiRoot();
      return (d && (d.referenceMonth || d.refMonth)) || '';
    },

    /**
     * 향후 비동기 전환을 위한 Promise 래퍼.
     * SharePoint 전환 시 본 함수만 fetch 구현으로 교체.
     */
    getKPIAsync: function () {
      // TODO(SharePoint): fetch + 캐시 정책 도입
      return Promise.resolve(_kpiRoot());
    },

    getPhotosAsync: function () {
      // TODO(SharePoint): fetch + 캐시 정책 도입
      return Promise.resolve(_photosRoot());
    },

    /** 어댑터 종류 식별 (전환 디버깅용) */
    kind: 'static-window-globals',
  };

  global.DATA_SOURCE = DATA_SOURCE;
})(window);
