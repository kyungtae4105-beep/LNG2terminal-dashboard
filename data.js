// 광양 LNG터미널 증설공사 대시보드 데이터
// 이 파일은 대시보드의 데이터 편집 탭을 통해 갱신됩니다.

window.DASHBOARD_DATA = {
  project: {
    name: "광양 제2 LNG터미널 증설공사",
    owner: "에너지건설 TF",
    report_period: "2025년 6월 ~ 2026년 3월",
    purpose: "에너지건설 TF 주요 지표 Dashboard 구축"
  },

  progress: {
    months: ["2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"],
    종합:   { plan: [61.65, 65.12, 68.83, 73.42, 77.27, 81.36, 84.86, 88.73, 91.96, 94.37], actual: [63.26, 66.98, 69.31, 72.3, 73.81, 77.79, 80.55, 82.2, 86.16, 88.99] },
    육상부: { plan: [56.16, 59.76, 63.43, 68.41, 73.13, 77.82, 81.84, 86.7, 90.73, 93.71], actual: [54.79, 58.63, 60.99, 63.62, 65.14, 70.23, 73.14, 75.09, 80.86, 84.9] },
    해상부: { plan: [73.06, 76.0, 79.67, 83.83, 85.88, 88.72, 91.15, 92.78, 94.38, 95.65], actual: [80.86, 84.06, 86.24, 90.35, 91.83, 93.5, 95.97, 96.7, 96.96, 97.3] },
    "154kV": { plan: [null, 81.16, 91.83, 95.42, 98.6, 96.67, 98.7, 99.9, 100.0, 100.0], actual: [null, 84.51, 92.44, 92.98, 94.2, 98.31, 98.31, 99.53, 100.0, 100.0] }
  },

  manpower: {
    months: ["2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"],
    종합:   { manager: [61, 68, 70, 73, 69, 68, 67, 71, 65, 63], partner: [640, 735, 675, 661, 713, 669, 651, 595, 574, 595] },
    육상부: { manager: [43, 46, 51, 51, 50, 48, 49, 55, 51, 51], partner: [520, 600, 559, 545, 618, 588, 603, 567, 540, 569] },
    해상부: { manager: [18, 18, 17, 20, 17, 18, 17, 15, 13, 11], partner: [120, 120, 106, 106, 90, 70, 42, 23, 30, 22] },
    "154kV": { manager: [null, 2, 2, 2, 2, 2, 1, 1, 1, 0], partner: [null, 10, 10, 10, 5, 11, 6, 5, 4, 0] }
  },

  no_accident_days: {
    months: ["2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"],
    육상부: [80, 111, 142, 172, 203, 233, 264, 295, 323, 354],
    해상부: [648, 679, 710, 740, 771, 801, 832, 863, 891, 922],
    "154kV": [null, 242, 273, 303, 334, 364, 395, 426, 454, null]
  },

  safety_audit_land: {
    months: ["2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"],
    추락:    [null, null, null, null, null, null, null, 77, 53, 62],
    전도:    [null, null, null, null, null, null, null, 90, 61, 70],
    "낙하/비래": [null, null, null, null, null, null, null, 48, 43, 44],
    감전:    [null, null, null, null, null, null, null, 34, 29, 40],
    "충돌/협착": [null, null, null, null, null, null, null, 39, 45, 33],
    "붕괴/도괴": [null, null, null, null, null, null, null, 13, 2, 6],
    "화재/폭발": [null, null, null, null, null, null, null, 17, 16, 17],
    질식:    [null, null, null, null, null, null, null, 0, 0, 0],
    기타:    [null, null, null, null, null, null, null, 122, 105, 141]
  },

  safety_edu_land: {
    months: ["2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"],
    "채용/작업변경": [null, null, null, null, null, null, null, 2857, 2981, 3205],
    특별교육:        [null, null, null, null, null, null, null, 8630, 8765, 9159],
    관리감독자:      [null, null, null, null, null, null, null, 2278, 2381, 2457],
    정기교육:        [null, null, null, null, null, null, null, 11351, 12366, 13371]
  },

  incident_summary: [
    { sub: "육상부", 공상: 2, 일반재해: 2, 중대재해: 0, 일반NearMiss: 0, 중대NearMiss: 4 },
    { sub: "해상부", 공상: 1, 일반재해: 3, 중대재해: 0, 일반NearMiss: 4, 중대NearMiss: 1 },
    { sub: "154kV", 공상: 0, 일반재해: 0, 중대재해: 0, 일반NearMiss: 1, 중대NearMiss: 0 }
  ],

  milestones: [
    { date: "2025-06-04", sub: "육상-전기", 공종: "전기", title: "주전기실 1층 Cable Tray 설치 착수", status: "착수" },
    { date: "2025-06-20", sub: "육상-토목", 공종: "토목", title: "벙커링부두 Pedestal Con’c 타설 完", status: "완료" },
    { date: "2025-06-25", sub: "육상-기계", 공종: "기계", title: "#8탱크 Inner Shell Plate 4단 설치 착수", status: "착수" },
    { date: "2025-06-28", sub: "육상-건축", 공종: "건축", title: "주전기실 2층 습식(블록) 공사 完", status: "완료" },
    { date: "2025-06-30", sub: "육상-기계", 공종: "기계", title: "#7탱크 Inner Shell Plate 6단 설치 착수", status: "착수" },
    { date: "2025-06-30", sub: "육상-건축", 공종: "건축", title: "본부빌딩 B 1층 습식(블록) 공사 完", status: "완료" },
    { date: "2025-07-01", sub: "육상-토목", 공종: "토목", title: "#7, 8탱크 Elec. Duct Bank 착수", status: "착수" },
    { date: "2025-07-02", sub: "육상-건축", 공종: "건축", title: "BOG Comp. Shelter 철골 지조립 및 설치 착수", status: "착수" },
    { date: "2025-07-14", sub: "육상-토목", 공종: "토목", title: "1터미널 SCV Wall Con’c 타설 完", status: "완료" },
    { date: "2025-07-15", sub: "육상-건축", 공종: "건축", title: "SOG Comp. Shelter 철골 지조립 및 설치 착수", status: "착수" },
    { date: "2025-07-22", sub: "육상-기계", 공종: "기계", title: "#7탱크 Inner Shell Plate 7단 설치 착수", status: "착수" },
    { date: "2025-07-25", sub: "육상-기계", 공종: "기계", title: "#8탱크 Inner Shell Plate 5단 설치 착수", status: "착수" },
    { date: "2025-07-31", sub: "육상-전기", 공종: "전기", title: "주전기실 2층 전기 Panel 설치 착수", status: "착수" },
    { date: "2025-08-28", sub: "전기/154kV", 공종: "전기", title: "LNG 전기실 TR측 154KV 케이블 접속 진행 完 - 변압기 종단 접속 및 케이블 중간접속 完 154KV 케이블 포설 完 - 1,2Line 케이블 포설", status: "완료" },
    { date: "2025-08-30", sub: "육상-토목", 공종: "토목", title: "1터미널 중화조 가시설 설치 完", status: "완료" },
    { date: "2025-08-30", sub: "육상-건축", 공종: "건축", title: "BOG 및 SOG Comp. Shelter 철골 설치 完", status: "완료" },
    { date: "2025-09-19", sub: "육상-토목", 공종: "토목", title: "LNG 부두 Working Platform 상부 Pedestal Con’c 타설 完", status: "완료" },
    { date: "2025-09-19", sub: "육상-전기", 공종: "전기", title: "주전기실 1층 수전용 Cable 포설 完", status: "완료" },
    { date: "2025-09-28", sub: "전기/154kV", 공종: "전기", title: "154KV 케이블 AC 내전압 테스트 完 - 1line : ~9.2, 2Line : ~9.3 주전기실↔SNG전기실 구간 점검/정리 - 케이블/선로점검, 표시찰 부착 - AC 내전압 시험기, 테스트 부싱, 발전기 반출", status: "완료" },
    { date: "2025-09-30", sub: "육상-건축", 공종: "건축", title: "주전기실 마감공사 90% 진행 및 Shelter류 철골설치 完", status: "완료" },
    { date: "2025-10-15", sub: "육상-기계", 공종: "기계", title: "#7탱크 Inner Shell Plate 9단 설치 착수", status: "착수" },
    { date: "2025-10-16", sub: "육상-토목", 공종: "토목", title: "주전기실 소방 지중배관 터파기 착수", status: "착수" },
    { date: "2025-10-22", sub: "육상-토목", 공종: "토목", title: "해상 JP(Joint Pier)-2 Pedestal 공사 착수", status: "착수" },
    { date: "2025-10-22", sub: "육상-건축", 공종: "건축", title: "주전기실 내외부 도장 完", status: "완료" },
    { date: "2025-10-27", sub: "육상-기계", 공종: "기계", title: "#8탱크 Inner Shell Plate 7단 설치 착수", status: "착수" },
    { date: "2025-10-27", sub: "육상-전기", 공종: "전기", title: "주전기실↔본부빌딩B 6.6kv Cable 포설 착수", status: "착수" },
    { date: "2025-10-30", sub: "육상-건축", 공종: "건축", title: "SOG Comp. Shelter 외부판넬 설치 完", status: "완료" },
    { date: "2025-10-31", sub: "육상-기계", 공종: "기계", title: "오버헤드크레인 설치 및 완성검사 完", status: "완료" },
    { date: "2025-11-07", sub: "육상-토목", 공종: "토목", title: "#8탱크 소방 지중배관 터파기 착수", status: "착수" },
    { date: "2025-11-07", sub: "육상-기계", 공종: "기계", title: "#7탱크 Inner Shell Plate 10단 설치 착수", status: "착수" },
    { date: "2025-11-12", sub: "육상-기계", 공종: "기계", title: "BOG Comp. 설치 착수", status: "착수" },
    { date: "2025-11-14", sub: "육상-토목", 공종: "토목", title: "해상 JP(Joint Pier)-2 Pedestal 설치 完", status: "완료" },
    { date: "2025-11-14", sub: "육상-전기", 공종: "전기", title: "본부빌딩 B 전기실 사용전 검사 完", status: "완료" },
    { date: "2025-11-14", sub: "육상-건축", 공종: "건축", title: "본부빌딩 B 옥상 누름 타설 完", status: "완료" },
    { date: "2025-11-19", sub: "육상-기계", 공종: "기계", title: "#8탱크 Inner Shell Plate 8단 설치 착수", status: "착수" },
    { date: "2025-11-28", sub: "해상-부두공", 공종: "부두공", title: "상부공 진행 - LNG부두 Fender 설치 中 - 벙커링부두 Fender 및 Catwalk 설치 完 전기방식 89% 설치", status: "완료" },
    { date: "2025-11-29", sub: "육상-건축", 공종: "건축", title: "주전기실 이중바닥재 및 금속공사 完", status: "완료" },
    { date: "2025-12-01", sub: "육상-토목", 공종: "토목", title: "주전기실 소방 지중배관 터파기 착수", status: "착수" },
    { date: "2025-12-01", sub: "육상-토목", 공종: "토목", title: "#7탱크 Small Opening Closing 착수", status: "착수" },
    { date: "2025-12-18", sub: "육상-건축", 공종: "건축", title: "Gate House 철근 콘크리트 공사 完", status: "완료" },
    { date: "2025-12-24", sub: "육상-기계", 공종: "기계", title: "BOG/SOG 압축기 설치 完", status: "완료" },
    { date: "2025-12-26", sub: "육상-기계", 공종: "기계", title: "#8탱크 Inner Shell Plate 9단 설치 착수", status: "착수" },
    { date: "2025-12-28", sub: "해상-부두공", 공종: "부두공", title: "상부공 진행 - LNG부두 Fender 및 Catwalk 설치 完 - Ladder 및 Handrail 설치 中 전기방식 97% 설치", status: "완료" },
    { date: "2025-12-28", sub: "전기/154kV", 공종: "전기", title: "케이블 포설 및 결선 - 비상발전기~전기실 구간, SNG전기실 등 공동가대 구간 비계 해체작업 完", status: "완료" },
    { date: "2025-12-30", sub: "육상-전기", 공종: "전기", title: "본부빌딩 B 전기실 6.6kV 수전 完", status: "완료" },
    { date: "2025-12-31", sub: "육상-기계", 공종: "기계", title: "#7탱크 Anchor Strap Upper Part 설치 착수", status: "착수" },
    { date: "2025-12-31", sub: "육상-건축", 공종: "건축", title: "본부빌딩 B 내부 도장 및 마감공사 完", status: "완료" },
    { date: "2026-01-10", sub: "육상-기계", 공종: "기계", title: "#7탱크 Large Opening Closing 착수", status: "착수" },
    { date: "2026-01-10", sub: "육상-기계", 공종: "기계", title: "탱크 Jib Crane 설치 完", status: "완료" },
    { date: "2026-01-13", sub: "육상-토목", 공종: "토목", title: "#7탱크 Small Opening PT-Step4 完", status: "완료" },
    { date: "2026-01-15", sub: "육상-전기", 공종: "전기", title: "#7탱크 Cable 포설 착수", status: "착수" },
    { date: "2026-01-22", sub: "육상-기계", 공종: "기계", title: "#8탱크 Inner Shell Plate 10단 설치 착수", status: "착수" },
    { date: "2026-01-29", sub: "육상-토목", 공종: "토목", title: "#8탱크 Small Opening PT-Step4 完", status: "완료" },
    { date: "2026-02-05", sub: "육상-기계", 공종: "기계", title: "#7탱크 Large Opening Closing 完", status: "완료" },
    { date: "2026-02-10", sub: "전기/154kV", 공종: "전기", title: "154kV 수전 完 (주전기실 154kV 수전)", status: "완료" },
    { date: "2026-02-11", sub: "육상-토목", 공종: "토목", title: "#7탱크 Large Opening 콘크리트 타설 完", status: "완료" },
    { date: "2026-02-12", sub: "해상-부두공", 공종: "부두공", title: "LNG부두 오일펜스 설치 完", status: "완료" },
    { date: "2026-02-13", sub: "육상-기계", 공종: "기계", title: "#7탱크 수압시험 착수", status: "착수" },
    { date: "2026-02-20", sub: "육상-기계", 공종: "기계", title: "#8탱크 Inner Shell Plate 10단 용접 完", status: "완료" },
    { date: "2026-02-28", sub: "육상-기계", 공종: "기계", title: "하역암 조립 및 설치 完", status: "완료" },
    { date: "2026-02-28", sub: "육상-기계", 공종: "기계", title: "Ground Flare 설치 完", status: "완료" },
    { date: "2026-03-04", sub: "육상-기계", 공종: "기계", title: "#7탱크 수압시험 完", status: "완료" },
    { date: "2026-03-04", sub: "육상-기계", 공종: "기계", title: "#7,8탱크 Jib Crane 완성검사 完", status: "완료" },
    { date: "2026-03-05", sub: "육상-토목", 공종: "토목", title: "#7탱크 Roof 도장 착수", status: "착수" },
    { date: "2026-03-11", sub: "육상-토목", 공종: "토목", title: "#7탱크 강선 인장 작업 完", status: "완료" },
    { date: "2026-03-14", sub: "육상-기계", 공종: "기계", title: "#7탱크 배수 및 내압시험 完", status: "완료" },
    { date: "2026-03-18", sub: "육상-기계", 공종: "기계", title: "#8탱크 Large Opening Closing 착수", status: "착수" },
    { date: "2026-03-25", sub: "육상-기계", 공종: "기계", title: "질소·공기 배관 내압시험 完", status: "완료" },
    { date: "2026-03-31", sub: "육상-건축", 공종: "건축", title: "Gate House 마감공사 完", status: "완료" }
  ],

  next_month_plan: [
    { date: "2026-04-06", 공종: "토목", title: "#7탱크 벽체 도장 착수" },
    { date: "2026-04-10", 공종: "전기", title: "주전기실 정전 및 마무리 작업 完" },
    { date: "2026-04-13", 공종: "기계", title: "#7탱크 LP Pump 설치 착수" },
    { date: "2026-04-17", 공종: "토목", title: "#8탱크 Large Opening 타설 完" },
    { date: "2026-04-20", 공종: "기계", title: "#8탱크 수압시험 충수 착수" },
    { date: "2026-04-21", 공종: "기계", title: "#7탱크 벽체 보온 설치 完" },
    { date: "2026-04-30", 공종: "기계", title: "1·2터미널 연결배관 작업 完" },
    { date: "2026-04-30", 공종: "건축", title: "해상 전기실 천정 설치 完" }
  ]
};
