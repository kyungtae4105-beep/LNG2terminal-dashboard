# -*- coding: utf-8 -*-
"""
data.js 시계열 확장:
- months: 2023-02 ~ 2026-03 (38개월, 누락월 포함)
- progress: 본계약 진척률 (2023-08~), 1차계약(2023-02~07)은 별도 보존
- manpower, safety_audit, safety_edu, no_accident_days 모두 확장
- 2023-2024 마일스톤은 tank78_section_lines에서 추출하여 보존
"""
import json
import os
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\14ZB95N\Desktop\대시보드"

# 1. 기존 data.js 파싱 (간단히 - JS 객체이지만 JSON에 가까움)
with open(os.path.join(ROOT, 'data.js'), 'r', encoding='utf-8') as f:
    data_content = f.read()
# window.DASHBOARD_DATA = {...};
# JS의 키가 quote 없거나 single quote 사용. 그대로 두고 일부 변경 후 저장.
# 우리는 새로운 data.js를 직접 작성하는 게 간단.

# 2. legacy KPI 로드
with open(os.path.join(ROOT, 'legacy_kpi_extracted.json'), 'r', encoding='utf-8') as f:
    legacy_obj = json.load(f)
legacy = legacy_obj['data']  # {YYYY-MM: {...}}

# 3. 통합 월 시퀀스 생성: 2023-02 ~ 2026-03
def gen_months(start, end):
    """start='2023-02', end='2026-03'"""
    sy, sm = map(int, start.split('-'))
    ey, em = map(int, end.split('-'))
    out = []
    y, m = sy, sm
    while (y, m) <= (ey, em):
        out.append(f'{y:04d}-{m:02d}')
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out

ALL_MONTHS = gen_months('2023-02', '2026-03')  # 38개월

# 4. 기존 2025-06~2026-03 데이터 (현재 data.js에서 그대로 유지)
EXISTING = {
    "2025-06": {
        "progress": {"종합": (61.65, 63.26), "육상부": (56.16, 54.79), "해상부": (73.06, 80.86), "154kV": (None, None)},
        "manpower": {"종합": (61, 640), "육상부": (43, 520), "해상부": (18, 120), "154kV": (None, None)},
        "no_accident": {"육상부": 80, "해상부": 648, "154kV": None},
    },
    "2025-07": {
        "progress": {"종합": (65.12, 66.98), "육상부": (59.76, 58.63), "해상부": (76.0, 84.06), "154kV": (81.16, 84.51)},
        "manpower": {"종합": (68, 735), "육상부": (46, 600), "해상부": (18, 120), "154kV": (2, 10)},
        "no_accident": {"육상부": 111, "해상부": 679, "154kV": 242},
    },
    "2025-08": {
        "progress": {"종합": (68.83, 69.31), "육상부": (63.43, 60.99), "해상부": (79.67, 86.24), "154kV": (91.83, 92.44)},
        "manpower": {"종합": (70, 675), "육상부": (51, 559), "해상부": (17, 106), "154kV": (2, 10)},
        "no_accident": {"육상부": 142, "해상부": 710, "154kV": 273},
    },
    "2025-09": {
        "progress": {"종합": (73.42, 72.3), "육상부": (68.41, 63.62), "해상부": (83.83, 90.35), "154kV": (95.42, 92.98)},
        "manpower": {"종합": (73, 661), "육상부": (51, 545), "해상부": (20, 106), "154kV": (2, 10)},
        "no_accident": {"육상부": 172, "해상부": 740, "154kV": 303},
    },
    "2025-10": {
        "progress": {"종합": (77.27, 73.81), "육상부": (73.13, 65.14), "해상부": (85.88, 91.83), "154kV": (98.6, 94.2)},
        "manpower": {"종합": (69, 713), "육상부": (50, 618), "해상부": (17, 90), "154kV": (2, 5)},
        "no_accident": {"육상부": 203, "해상부": 771, "154kV": 334},
    },
    "2025-11": {
        "progress": {"종합": (81.36, 77.79), "육상부": (77.82, 70.23), "해상부": (88.72, 93.5), "154kV": (96.67, 98.31)},
        "manpower": {"종합": (68, 669), "육상부": (48, 588), "해상부": (18, 70), "154kV": (2, 11)},
        "no_accident": {"육상부": 233, "해상부": 801, "154kV": 364},
    },
    "2025-12": {
        "progress": {"종합": (84.86, 80.55), "육상부": (81.84, 73.14), "해상부": (91.15, 95.97), "154kV": (98.7, 98.31)},
        "manpower": {"종합": (67, 651), "육상부": (49, 603), "해상부": (17, 42), "154kV": (1, 6)},
        "no_accident": {"육상부": 264, "해상부": 832, "154kV": 395},
    },
    "2026-01": {
        "progress": {"종합": (88.73, 82.2), "육상부": (86.7, 75.09), "해상부": (92.78, 96.7), "154kV": (99.9, 99.53)},
        "manpower": {"종합": (71, 595), "육상부": (55, 567), "해상부": (15, 23), "154kV": (1, 5)},
        "no_accident": {"육상부": 295, "해상부": 863, "154kV": 426},
    },
    "2026-02": {
        "progress": {"종합": (91.96, 86.16), "육상부": (90.73, 80.86), "해상부": (94.38, 96.96), "154kV": (100.0, 100.0)},
        "manpower": {"종합": (65, 574), "육상부": (51, 540), "해상부": (13, 30), "154kV": (1, 4)},
        "no_accident": {"육상부": 323, "해상부": 891, "154kV": 454},
    },
    "2026-03": {
        "progress": {"종합": (94.37, 88.99), "육상부": (93.71, 84.9), "해상부": (95.65, 97.3), "154kV": (100.0, 100.0)},
        "manpower": {"종합": (63, 595), "육상부": (51, 569), "해상부": (11, 22), "154kV": (0, 0)},
        "no_accident": {"육상부": 354, "해상부": 922, "154kV": None},
    },
}

# 기존 safety_audit_land (2026-01~03)
SAFETY_AUDIT_EXISTING = {
    "2026-01": {"추락": 77, "전도": 90, "낙하/비래": 48, "감전": 34, "충돌/협착": 39, "붕괴/도괴": 13, "화재/폭발": 17, "질식": 0, "기타": 122},
    "2026-02": {"추락": 53, "전도": 61, "낙하/비래": 43, "감전": 29, "충돌/협착": 45, "붕괴/도괴": 2, "화재/폭발": 16, "질식": 0, "기타": 105},
    "2026-03": {"추락": 62, "전도": 70, "낙하/비래": 44, "감전": 40, "충돌/협착": 33, "붕괴/도괴": 6, "화재/폭발": 17, "질식": 0, "기타": 141},
}
SAFETY_EDU_EXISTING = {
    "2026-01": {"채용/작업변경": 2857, "특별교육": 8630, "관리감독자": 2278, "정기교육": 11351},
    "2026-02": {"채용/작업변경": 2981, "특별교육": 8765, "관리감독자": 2381, "정기교육": 12366},
    "2026-03": {"채용/작업변경": 3205, "특별교육": 9159, "관리감독자": 2457, "정기교육": 13371},
}

# 5. 시리즈 빌더
def build_series(field_extractor, default=None):
    """field_extractor(month_key) → value or None"""
    return [field_extractor(m) for m in ALL_MONTHS]

def _safe_dict(d, key):
    v = d.get(key)
    return v if isinstance(v, dict) else {}

def progress_actual(sub):
    """sub: '종합'/'육상부'/'해상부'/'154kV'
    메인 시리즈는 2024-01부터 (제2 LNG터미널 종합공정률 기준 일관성).
    2023-08~11은 tank78(본계약 초기) → 별도 phase_b 시리즈.
    """
    def get(m):
        if m in EXISTING:
            v = EXISTING[m]['progress'].get(sub)
            return v[1] if v else None
        if m in legacy:
            yr, mo = m.split('-')
            if yr == '2023':
                return None  # 2023년은 메인 시리즈에 포함 안 함 (별도)
            d = legacy[m]
            tank78 = _safe_dict(d, 'tank78')
            tank78_total = _safe_dict(d, 'tank78_total')
            if sub == '종합':
                v = tank78_total.get('progress_actual')
                if v is not None:
                    return v
                return tank78.get('progress_actual')
            return None
        return None
    return get

def progress_plan(sub):
    """plan_pct를 사용. 없으면 plan_ratio로부터 추정."""
    def get(m):
        if m in EXISTING:
            v = EXISTING[m]['progress'].get(sub)
            return v[0] if v else None
        if m in legacy:
            yr, mo = m.split('-')
            if yr == '2023':
                return None
            if sub != '종합':
                return None
            d = legacy[m]
            tank78_total = _safe_dict(d, 'tank78_total')
            tank78 = _safe_dict(d, 'tank78')
            plan = tank78_total.get('progress_plan_pct') or tank78.get('progress_plan_pct')
            if plan is not None:
                return plan
            actual = tank78_total.get('progress_actual') or tank78.get('progress_actual')
            ratio = tank78_total.get('progress_plan_ratio') or tank78.get('progress_plan_ratio')
            if actual and ratio:
                if abs(ratio) < 50:
                    return round(actual - ratio, 2)
                return round(actual / ratio * 100, 2)
            return None
        return None
    return get

def manpower_field(sub, idx):
    """idx 0=manager, 1=partner"""
    def get(m):
        if m in EXISTING:
            v = EXISTING[m]['manpower'].get(sub)
            return v[idx] if v else None
        if m in legacy and sub == '종합':
            d = legacy[m]
            tank78_total = _safe_dict(d, 'tank78_total')
            tank78 = _safe_dict(d, 'tank78')
            # tank78_total이 종합적
            if idx == 0:
                return tank78_total.get('manpower_manager') or tank78.get('manpower_manager')
            else:
                return tank78_total.get('manpower_partner') or tank78.get('manpower_partner')
        return None
    return get

def no_accident_field(sub):
    def get(m):
        if m in EXISTING:
            return EXISTING[m]['no_accident'].get(sub)
        return None
    return get

def safety_audit_field(cat):
    def get(m):
        if m in SAFETY_AUDIT_EXISTING:
            return SAFETY_AUDIT_EXISTING[m].get(cat)
        if m in legacy:
            sa = legacy[m].get('safety_audit') or {}
            return sa.get(cat)
        return None
    return get

def safety_edu_field(cat):
    def get(m):
        if m in SAFETY_EDU_EXISTING:
            return SAFETY_EDU_EXISTING[m].get(cat)
        return None
    return get

# 6. progress, manpower 등 시리즈 생성
progress = {
    'months': ALL_MONTHS,
}
for sub in ['종합', '육상부', '해상부', '154kV']:
    progress[sub] = {
        'plan': build_series(progress_plan(sub)),
        'actual': build_series(progress_actual(sub)),
    }

manpower = {
    'months': ALL_MONTHS,
}
for sub in ['종합', '육상부', '해상부', '154kV']:
    manpower[sub] = {
        'manager': build_series(manpower_field(sub, 0)),
        'partner': build_series(manpower_field(sub, 1)),
    }

no_accident_days = {
    'months': ALL_MONTHS,
    '육상부': build_series(no_accident_field('육상부')),
    '해상부': build_series(no_accident_field('해상부')),
    '154kV': build_series(no_accident_field('154kV')),
}

safety_audit_land = {
    'months': ALL_MONTHS,
    '추락': build_series(safety_audit_field('추락')),
    '전도': build_series(safety_audit_field('전도')),
    '낙하/비래': build_series(safety_audit_field('낙하·비래')),
    '감전': build_series(safety_audit_field('감전')),
    '충돌/협착': build_series(safety_audit_field('충돌·협착')),
    '붕괴/도괴': build_series(safety_audit_field('붕괴·도괴')),
    '화재/폭발': build_series(safety_audit_field('화재·폭발')),
    '질식': build_series(safety_audit_field('질식')),
    '기타': build_series(safety_audit_field('기타')),
}
# 기존 키 호환
def _safety_audit_existing_key(m, k):
    return SAFETY_AUDIT_EXISTING.get(m, {}).get(k)
for k in ['낙하/비래', '충돌/협착', '붕괴/도괴', '화재/폭발']:
    series = []
    for m in ALL_MONTHS:
        if m in SAFETY_AUDIT_EXISTING:
            series.append(SAFETY_AUDIT_EXISTING[m][k])
        elif m in legacy:
            sa = legacy[m].get('safety_audit') or {}
            # legacy uses 낙하·비래 (·) but existing uses 낙하/비래 (/) - unify
            alt_key = k.replace('/', '·')
            series.append(sa.get(alt_key))
        else:
            series.append(None)
    safety_audit_land[k] = series

safety_edu_land = {
    'months': ALL_MONTHS,
    '채용/작업변경': build_series(safety_edu_field('채용/작업변경')),
    '특별교육': build_series(safety_edu_field('특별교육')),
    '관리감독자': build_series(safety_edu_field('관리감독자')),
    '정기교육': build_series(safety_edu_field('정기교육')),
}

# 7. 2023년 #7,8 탱크 단독 진척률 → 별도 보존 (1차계약 + 본계약 초기)
legacy_2023_progress = {
    'months': [],
    'phase': [],          # '1차계약' / '본계약'
    'tank78_actual': [],  # tank78의 진척률
    'tank78_plan_ratio': [],
}
for m in ALL_MONTHS:
    yr, mo = m.split('-')
    if yr == '2023' and m in legacy:
        d = legacy[m]
        tank78 = _safe_dict(d, 'tank78')
        legacy_2023_progress['months'].append(m)
        legacy_2023_progress['phase'].append('1차계약' if int(mo) <= 7 else '본계약')
        legacy_2023_progress['tank78_actual'].append(tank78.get('progress_actual'))
        legacy_2023_progress['tank78_plan_ratio'].append(tank78.get('progress_plan_ratio'))

phase1_progress = legacy_2023_progress  # 호환 명칭

# 8. tank6 진척률 (1터미널 마감 - 참고용) → 별도 보존
tank6_progress = {
    'months': [],
    '진척률': [],
}
for m in ALL_MONTHS:
    if m in legacy:
        d = legacy[m]
        tank6 = _safe_dict(d, 'tank6')
        v = tank6.get('progress_actual')
        if v is not None:
            tank6_progress['months'].append(m)
            tank6_progress['진척률'].append(v)

# 9. 마일스톤: 2023-2024년은 tank78_section_lines에서 추출 (수동 매핑)
# 사용자 검증 가능한 수준으로 자동 추출. 패턴:  '完(MM/DD)' 또는 '완료', '착수' 키워드 + 날짜
def parse_legacy_milestones(month_key, lines):
    """tank78_section_lines를 분석하여 완료/착수 마일스톤 추출."""
    mss = []
    yr, mo = month_key.split('-')
    yr_short = yr[2:]
    # 라인을 먼저 합쳐서 복합 토큰 만들기
    full = ' '.join(lines)
    # '完' 또는 '진행中', '착수' 등의 패턴
    # "탱크 강관파일 항타 (~3/3_94% 진행)" 등
    # 간단히 구간을 찾는 정규식: <텍스트> (날짜 또는 完(M/D))
    # 너무 복잡 - 일단 빈 리스트 반환하고, 마일스톤은 별도 파싱
    return mss

legacy_milestones = []
# 자동 추출은 fragmented 텍스트 때문에 정확도가 낮음.
# 대신 핵심 메시지만 텍스트 그대로 보존 (사용자가 검토 후 수동 보강 가능).
# 우선 각 월의 #7,8 탱크 핵심 마일스톤을 수동으로 정의:
manual_legacy_milestones = [
    # 2023년 (1차 계약 - 강관파일/지반개량/콘크리트 기초)
    {"date": "2023-02-23", "sub": "육상-토목", "공종": "토목", "title": "[1차계약] #7탱크 강관파일 항타 진행 (94% 완료)", "status": "진행"},
    {"date": "2023-03-03", "sub": "육상-토목", "공종": "토목", "title": "[1차계약] #7탱크 강관파일 항타 完", "status": "완료"},
    {"date": "2023-06-16", "sub": "육상-토목", "공종": "토목", "title": "[1차계약] #8탱크 강관파일 항타 完", "status": "완료"},
    {"date": "2023-07-31", "sub": "육상-토목", "공종": "토목", "title": "[1차계약] 설비구간 지반개량공사 完", "status": "완료"},
    # 2023-08~ (본계약 시작)
    {"date": "2023-08-01", "sub": "전체", "공종": "기획", "title": "[본계약] #7,8탱크 본격 증설공사 착수", "status": "착수"},
    {"date": "2023-09-22", "sub": "해상-부두공", "공종": "부두공", "title": "해상부 공사 착수", "status": "착수"},
    {"date": "2024-01-29", "sub": "육상-토목", "공종": "토목", "title": "#6탱크 Large Opening 콘크리트 타설 (1터미널 마감)", "status": "완료"},
    {"date": "2024-01-30", "sub": "육상-기계", "공종": "기계", "title": "#6탱크 수압시험 충수", "status": "완료"},
    {"date": "2024-06-24", "sub": "육상-기계", "공종": "기계", "title": "#6탱크 LP LNG Pump 기동 Test (1터미널 종료)", "status": "완료"},
    {"date": "2024-06-30", "sub": "육상-기계", "공종": "기계", "title": "#6탱크(1터미널) 공정률 100% 달성", "status": "완료"},
    {"date": "2024-07-24", "sub": "육상-안전", "공종": "안전", "title": "제2 LNG터미널 무재해 일수 카운트 시작 (~24.07.24)", "status": "착수"},
    {"date": "2024-09-13", "sub": "육상-토목", "공종": "토목", "title": "#7탱크 Roof 1단 2차 Concrete 타설", "status": "완료"},
    {"date": "2024-09-26", "sub": "육상-토목", "공종": "토목", "title": "Process P/R 기초 거푸집 조립", "status": "진행"},
    {"date": "2024-11-12", "sub": "육상-토목", "공종": "토목", "title": "#7탱크 Roof 2단 3차 Concrete 타설", "status": "완료"},
    {"date": "2024-11-19", "sub": "육상-토목", "공종": "토목", "title": "#8탱크 Ring Beam Concrete 타설", "status": "완료"},
    {"date": "2024-11-23", "sub": "육상-토목", "공종": "토목", "title": "주전기실 독립기초 Concrete 타설", "status": "완료"},
]

# 10. 기존 milestones (그대로 유지)
EXISTING_MILESTONES = [
    {"date": "2025-06-04", "sub": "육상-전기", "공종": "전기", "title": "주전기실 1층 Cable Tray 설치 착수", "status": "착수"},
    {"date": "2025-06-20", "sub": "육상-토목", "공종": "토목", "title": "벙커링부두 Pedestal Con'c 타설 完", "status": "완료"},
    {"date": "2025-06-25", "sub": "육상-기계", "공종": "기계", "title": "#8탱크 Inner Shell Plate 4단 설치 착수", "status": "착수"},
    {"date": "2025-06-28", "sub": "육상-건축", "공종": "건축", "title": "주전기실 2층 습식(블록) 공사 完", "status": "완료"},
    {"date": "2025-06-30", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 Inner Shell Plate 6단 설치 착수", "status": "착수"},
    {"date": "2025-06-30", "sub": "육상-건축", "공종": "건축", "title": "본부빌딩 B 1층 습식(블록) 공사 完", "status": "완료"},
    {"date": "2025-07-01", "sub": "육상-토목", "공종": "토목", "title": "#7, 8탱크 Elec. Duct Bank 착수", "status": "착수"},
    {"date": "2025-07-02", "sub": "육상-건축", "공종": "건축", "title": "BOG Comp. Shelter 철골 지조립 및 설치 착수", "status": "착수"},
    {"date": "2025-07-14", "sub": "육상-토목", "공종": "토목", "title": "1터미널 SCV Wall Con'c 타설 完", "status": "완료"},
    {"date": "2025-07-15", "sub": "육상-건축", "공종": "건축", "title": "SOG Comp. Shelter 철골 지조립 및 설치 착수", "status": "착수"},
    {"date": "2025-07-22", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 Inner Shell Plate 7단 설치 착수", "status": "착수"},
    {"date": "2025-07-25", "sub": "육상-기계", "공종": "기계", "title": "#8탱크 Inner Shell Plate 5단 설치 착수", "status": "착수"},
    {"date": "2025-07-31", "sub": "육상-전기", "공종": "전기", "title": "주전기실 2층 전기 Panel 설치 착수", "status": "착수"},
    {"date": "2025-08-28", "sub": "전기/154kV", "공종": "전기", "title": "LNG 전기실 TR측 154KV 케이블 접속 진행 完", "status": "완료"},
    {"date": "2025-08-30", "sub": "육상-토목", "공종": "토목", "title": "1터미널 중화조 가시설 설치 完", "status": "완료"},
    {"date": "2025-08-30", "sub": "육상-건축", "공종": "건축", "title": "BOG 및 SOG Comp. Shelter 철골 설치 完", "status": "완료"},
    {"date": "2025-09-19", "sub": "육상-토목", "공종": "토목", "title": "LNG 부두 Working Platform 상부 Pedestal Con'c 타설 完", "status": "완료"},
    {"date": "2025-09-19", "sub": "육상-전기", "공종": "전기", "title": "주전기실 1층 수전용 Cable 포설 完", "status": "완료"},
    {"date": "2025-09-28", "sub": "전기/154kV", "공종": "전기", "title": "154KV 케이블 AC 내전압 테스트 完", "status": "완료"},
    {"date": "2025-09-30", "sub": "육상-건축", "공종": "건축", "title": "주전기실 마감공사 90% 진행 및 Shelter류 철골설치 完", "status": "완료"},
    {"date": "2025-10-15", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 Inner Shell Plate 9단 설치 착수", "status": "착수"},
    {"date": "2025-10-16", "sub": "육상-토목", "공종": "토목", "title": "주전기실 소방 지중배관 터파기 착수", "status": "착수"},
    {"date": "2025-10-22", "sub": "육상-토목", "공종": "토목", "title": "해상 JP(Joint Pier)-2 Pedestal 공사 착수", "status": "착수"},
    {"date": "2025-10-22", "sub": "육상-건축", "공종": "건축", "title": "주전기실 내외부 도장 完", "status": "완료"},
    {"date": "2025-10-27", "sub": "육상-기계", "공종": "기계", "title": "#8탱크 Inner Shell Plate 7단 설치 착수", "status": "착수"},
    {"date": "2025-10-27", "sub": "육상-전기", "공종": "전기", "title": "주전기실↔본부빌딩B 6.6kv Cable 포설 착수", "status": "착수"},
    {"date": "2025-10-30", "sub": "육상-건축", "공종": "건축", "title": "SOG Comp. Shelter 외부판넬 설치 完", "status": "완료"},
    {"date": "2025-10-31", "sub": "육상-기계", "공종": "기계", "title": "오버헤드크레인 설치 및 완성검사 完", "status": "완료"},
    {"date": "2025-11-07", "sub": "육상-토목", "공종": "토목", "title": "#8탱크 소방 지중배관 터파기 착수", "status": "착수"},
    {"date": "2025-11-07", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 Inner Shell Plate 10단 설치 착수", "status": "착수"},
    {"date": "2025-11-12", "sub": "육상-기계", "공종": "기계", "title": "BOG Comp. 설치 착수", "status": "착수"},
    {"date": "2025-11-14", "sub": "육상-토목", "공종": "토목", "title": "해상 JP(Joint Pier)-2 Pedestal 설치 完", "status": "완료"},
    {"date": "2025-11-14", "sub": "육상-전기", "공종": "전기", "title": "본부빌딩 B 전기실 사용전 검사 完", "status": "완료"},
    {"date": "2025-11-14", "sub": "육상-건축", "공종": "건축", "title": "본부빌딩 B 옥상 누름 타설 完", "status": "완료"},
    {"date": "2025-11-19", "sub": "육상-기계", "공종": "기계", "title": "#8탱크 Inner Shell Plate 8단 설치 착수", "status": "착수"},
    {"date": "2025-11-28", "sub": "해상-부두공", "공종": "부두공", "title": "상부공 진행 - LNG부두 Fender 설치 中", "status": "완료"},
    {"date": "2025-11-29", "sub": "육상-건축", "공종": "건축", "title": "주전기실 이중바닥재 및 금속공사 完", "status": "완료"},
    {"date": "2025-12-01", "sub": "육상-토목", "공종": "토목", "title": "주전기실 소방 지중배관 터파기 착수", "status": "착수"},
    {"date": "2025-12-01", "sub": "육상-토목", "공종": "토목", "title": "#7탱크 Small Opening Closing 착수", "status": "착수"},
    {"date": "2025-12-18", "sub": "육상-건축", "공종": "건축", "title": "Gate House 철근 콘크리트 공사 完", "status": "완료"},
    {"date": "2025-12-24", "sub": "육상-기계", "공종": "기계", "title": "BOG/SOG 압축기 설치 完", "status": "완료"},
    {"date": "2025-12-26", "sub": "육상-기계", "공종": "기계", "title": "#8탱크 Inner Shell Plate 9단 설치 착수", "status": "착수"},
    {"date": "2025-12-28", "sub": "해상-부두공", "공종": "부두공", "title": "상부공 진행 - LNG부두 Fender 및 Catwalk 설치 完", "status": "완료"},
    {"date": "2025-12-28", "sub": "전기/154kV", "공종": "전기", "title": "케이블 포설 및 결선 - 비상발전기~전기실 구간 완료", "status": "완료"},
    {"date": "2025-12-30", "sub": "육상-전기", "공종": "전기", "title": "본부빌딩 B 전기실 6.6kV 수전 完", "status": "완료"},
    {"date": "2025-12-31", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 Anchor Strap Upper Part 설치 착수", "status": "착수"},
    {"date": "2025-12-31", "sub": "육상-건축", "공종": "건축", "title": "본부빌딩 B 내부 도장 및 마감공사 完", "status": "완료"},
    {"date": "2026-01-10", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 Large Opening Closing 착수", "status": "착수"},
    {"date": "2026-01-10", "sub": "육상-기계", "공종": "기계", "title": "탱크 Jib Crane 설치 完", "status": "완료"},
    {"date": "2026-01-13", "sub": "육상-토목", "공종": "토목", "title": "#7탱크 Small Opening PT-Step4 完", "status": "완료"},
    {"date": "2026-01-15", "sub": "육상-전기", "공종": "전기", "title": "#7탱크 Cable 포설 착수", "status": "착수"},
    {"date": "2026-01-22", "sub": "육상-기계", "공종": "기계", "title": "#8탱크 Inner Shell Plate 10단 설치 착수", "status": "착수"},
    {"date": "2026-01-29", "sub": "육상-토목", "공종": "토목", "title": "#8탱크 Small Opening PT-Step4 完", "status": "완료"},
    {"date": "2026-02-05", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 Large Opening Closing 完", "status": "완료"},
    {"date": "2026-02-10", "sub": "전기/154kV", "공종": "전기", "title": "154kV 수전 完 (주전기실 154kV 수전)", "status": "완료"},
    {"date": "2026-02-11", "sub": "육상-토목", "공종": "토목", "title": "#7탱크 Large Opening 콘크리트 타설 完", "status": "완료"},
    {"date": "2026-02-12", "sub": "해상-부두공", "공종": "부두공", "title": "LNG부두 오일펜스 설치 完", "status": "완료"},
    {"date": "2026-02-13", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 수압시험 착수", "status": "착수"},
    {"date": "2026-02-20", "sub": "육상-기계", "공종": "기계", "title": "#8탱크 Inner Shell Plate 10단 용접 完", "status": "완료"},
    {"date": "2026-02-28", "sub": "육상-기계", "공종": "기계", "title": "하역암 조립 및 설치 完", "status": "완료"},
    {"date": "2026-02-28", "sub": "육상-기계", "공종": "기계", "title": "Ground Flare 설치 完", "status": "완료"},
    {"date": "2026-03-04", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 수압시험 完", "status": "완료"},
    {"date": "2026-03-04", "sub": "육상-기계", "공종": "기계", "title": "#7,8탱크 Jib Crane 완성검사 完", "status": "완료"},
    {"date": "2026-03-05", "sub": "육상-토목", "공종": "토목", "title": "#7탱크 Roof 도장 착수", "status": "착수"},
    {"date": "2026-03-11", "sub": "육상-토목", "공종": "토목", "title": "#7탱크 강선 인장 작업 完", "status": "완료"},
    {"date": "2026-03-14", "sub": "육상-기계", "공종": "기계", "title": "#7탱크 배수 및 내압시험 完", "status": "완료"},
    {"date": "2026-03-18", "sub": "육상-기계", "공종": "기계", "title": "#8탱크 Large Opening Closing 착수", "status": "착수"},
    {"date": "2026-03-25", "sub": "육상-기계", "공종": "기계", "title": "질소·공기 배관 내압시험 完", "status": "완료"},
    {"date": "2026-03-31", "sub": "육상-건축", "공종": "건축", "title": "Gate House 마감공사 完", "status": "완료"},
]

all_milestones = manual_legacy_milestones + EXISTING_MILESTONES
all_milestones.sort(key=lambda x: x['date'])

# 11. 기존 incident_summary, next_month_plan 보존
incident_summary = [
    {"sub": "육상부", "공상": 2, "일반재해": 2, "중대재해": 0, "일반NearMiss": 0, "중대NearMiss": 4},
    {"sub": "해상부", "공상": 1, "일반재해": 3, "중대재해": 0, "일반NearMiss": 4, "중대NearMiss": 1},
    {"sub": "154kV", "공상": 0, "일반재해": 0, "중대재해": 0, "일반NearMiss": 1, "중대NearMiss": 0},
]
next_month_plan = [
    {"date": "2026-04-06", "공종": "토목", "title": "#7탱크 벽체 도장 착수"},
    {"date": "2026-04-10", "공종": "전기", "title": "주전기실 정전 및 마무리 작업 完"},
    {"date": "2026-04-13", "공종": "기계", "title": "#7탱크 LP Pump 설치 착수"},
    {"date": "2026-04-17", "공종": "토목", "title": "#8탱크 Large Opening 타설 完"},
    {"date": "2026-04-20", "공종": "기계", "title": "#8탱크 수압시험 충수 착수"},
    {"date": "2026-04-21", "공종": "기계", "title": "#7탱크 벽체 보온 설치 完"},
    {"date": "2026-04-30", "공종": "기계", "title": "1·2터미널 연결배관 작업 完"},
    {"date": "2026-04-30", "공종": "건축", "title": "해상 전기실 천정 설치 完"},
]

# 12. 최종 객체
DASHBOARD_DATA = {
    "project": {
        "name": "광양 제2 LNG터미널 증설공사",
        "owner": "에너지건설 TF",
        "report_period": "2023년 2월 ~ 2026년 3월",
        "purpose": "에너지건설 TF 주요 지표 Dashboard 구축",
        "phases": [
            {"name": "1차 계약", "start": "2023-02", "end": "2023-07", "desc": "기초공사 (강관파일·지반개량)"},
            {"name": "본 계약", "start": "2023-08", "end": None, "desc": "#7,8탱크 본격 증설공사"},
        ],
        "data_gaps": ["2023-12", "2024-02", "2024-10", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05"],
        "data_gap_reason": {
            "2023-12": "보고서 DRM 보호로 추출 불가",
            "2024-02": "보고서 DRM 보호로 추출 불가",
            "2024-10": "보고서 DRM 보호로 추출 불가",
            "2024-12": "보고서 미보유",
            "2025-01": "보고서 미보유",
            "2025-02": "보고서 미보유",
            "2025-03": "보고서 미보유",
            "2025-04": "보고서 미보유",
            "2025-05": "보고서 미보유",
        }
    },
    "progress": progress,
    "manpower": manpower,
    "no_accident_days": no_accident_days,
    "safety_audit_land": safety_audit_land,
    "safety_edu_land": safety_edu_land,
    "incident_summary": incident_summary,
    "phase1_progress": phase1_progress,  # 1차계약 (2023-02~07) 별도 보존
    "tank6_progress": tank6_progress,    # 1터미널 #6탱크 마감 진척률 (참고)
    "milestones": all_milestones,
    "next_month_plan": next_month_plan,
}

# 13. data.js 파일로 작성 (JS 형식)
js_out = "// 광양 제2 LNG터미널 증설공사 대시보드 데이터\n"
js_out += "// 보고기간: 2023년 2월 ~ 2026년 3월 (38개월, 일부 갭 포함)\n"
js_out += "// 갭 사유: DRM 보호 또는 보고서 미보유 (data_gap_reason 참조)\n\n"
js_out += "window.DASHBOARD_DATA = "
js_out += json.dumps(DASHBOARD_DATA, ensure_ascii=False, indent=2)
js_out += ";\n"

with open(os.path.join(ROOT, 'data.js'), 'w', encoding='utf-8') as f:
    f.write(js_out)

print("[DONE] data.js generated")
print(f"  Total months: {len(ALL_MONTHS)}")
print(f"  Milestones: {len(all_milestones)}")
print(f"  Phase1 months: {len(phase1_progress['months'])}")
print(f"  tank6 months: {len(tank6_progress['months'])}")
# 진척률 통계
print(f"\n  종합 진척률 (actual):")
for m, v in zip(ALL_MONTHS, progress['종합']['actual']):
    if v is not None:
        print(f"    {m}: {v}")
