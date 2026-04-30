import json, os, shutil, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\kyungtae\OneDrive - POSCO INTERNATIONAL\바탕 화면\대시보드"
EXTRACT = os.path.join(ROOT, "ppt_extract")
PHOTOS = os.path.join(ROOT, "photos")

# Manually curated mapping based on the inspect output:
# For each "photo slide" the captions are listed in display order
PHOTO_PAGES = {
    "01월": [
        {
            "slide": 6, "category": "육상부", "type": "공사사진",
            "title": "공사 사진 (육상부) - 1월",
            "images_start": 3,  # skip the first 3 header images (image1.jpeg, image2.png, image3.png)
            "captions": [
                "해상 Module (WP-03B) 설치 完 ('26.01.20)",
                "벙커링3부두 로딩암(2103LA) 설치 ('26.01.27)",
                "LNG2부두 Jetty 전기실 데크 플레이트 설치공사 ('26.01.30)",
                "벙커링3부두 로딩암(2104L) 설치 ('26.01.30)",
                "제2 LNG터미널 육상부 전경 ('26.01.30)",
                "제2 LNG터미널 해상 Jetty 상부시설 전경 ('26.01.30)",
            ]
        },
        {
            "slide": 7, "category": "육상부", "type": "안전점검",
            "title": "안전점검 사진 (육상부) - 1월",
            "images_start": 2,
            "captions": [
                "상주건설장비 점검 (1.28)",
                "안전보건협의체 회의 (1.28)",
                "정기안전보건교육 (1.21~1.23)",
                "PM주관 타운홀 미팅 (1.27)",
                "자율안전컨설팅 (1.20)",
                "동절기 어묵 꼬치 나눔 행사 (1.21)",
                "노사합동점검 (1.6)",
                "한랭질환 예방 건강상담 (1.12)",
            ]
        },
        {
            "slide": 8, "category": "해상부", "type": "공정사진",
            "title": "공정사진 (항만공사) - 1월",
            "images_start": 2,
            "captions": [
                "해상부 외부 전경 ('26.01.10)",
                "해상부 외부 전경 ('26.01.10)",
                "LNG MD-06 오일휀스 설치 ('26.01.19)",
                "LNG MD-03 LADDER 설치 ('26.01.13)",
                "LNG MD-01 자켓 청소 ('26.01.07)",
                "LNG CP-01 테이프방식 ('26.01.06)",
            ]
        },
        {
            "slide": 9, "category": "해상부", "type": "안전점검",
            "title": "안전점검 사진 (항만공사) - 1월",
            "images_start": 2,
            "captions": [
                "동절기 안전점검 ('26.01.08)",
                "선박 홋줄 특별점검 ('26.01.08)",
                "위험성평가 사전회의 ('26.01.14)",
                "중처법 이행현황 월간점검 ('26.01.14)",
                "'26년 중점관리사항 회의 ('26.01.15)",
                "안전기원제 ('26.01.16)",
                "월간안전점검 ('26.01.20)",
                "부지항만사업단장 점검 ('26.01.23)",
            ]
        },
        {
            "slide": 10, "category": "154kV", "type": "공정사진",
            "title": "공정사진 (154kV 수전공사) - 1월",
            "images_start": 2,
            "captions": [
                "154kV 외부전경",
                "154kV 외부전경",
                "연료탱크 안전발판/사다리 설치 ('26.01.12)",
                "판넬 하부 마감처리 ('25.01.05)",
                "LNG 2터미널 CABLE 입선/결선 ('26.01.22)",
                "SNG 1전기실 연소방재 ('26.01.22)",
            ]
        },
        {
            "slide": 11, "category": "154kV", "type": "안전점검",
            "title": "안전점검 사진 (154kV 수전공사) - 1월",
            "images_start": 2,
            "captions": [
                "주간 특별안전점검 [전도사고 예방] ('26.01.22)",
                "순회점검 ('26.01.01~'26.01.31)",
                "주간 특별안전점검 [중량물 취급 작업안전] ('26.01.15)",
                "정기안전보건교육 ('26.01.15)",
                "안전보건협의체 ('26.01.13)",
                "고위험작업 집중안전관리 ('26.01.14)",
                "주간 특별안전점검 [추락사고 예방] ('26.01.08)",
                "합동안전점검 ('26.01.13)",
            ]
        },
    ],
    "02월": [
        {
            "slide": 6, "category": "육상부", "type": "공사사진",
            "title": "공사 사진 (육상부) - 2월",
            "images_start": 3,
            "captions": [
                "LNG2부두 언로딩암(2101LA) 선적 ('26.02.09)",
                "#7탱크 Hydrostatic Test 착수 ('26.02.13)",
                "LNG2부두 언로딩암 설치 ('26.02.13)",
                "벙커링3부두 언로딩암 설치 ('26.02.13)",
                "제2 LNG터미널 육상부 전경 ('26.02.28)",
                "제2 LNG터미널 해상 Jetty 전경 ('26.02.28)",
            ]
        },
        {
            "slide": 7, "category": "육상부", "type": "안전점검",
            "title": "안전점검 사진 (육상부) - 2월",
            "images_start": 2,
            "captions": [
                "상주건설장비 점검 ('26.02.26)",
                "산업안전보건위원회 ('26.02.26)",
                "정기안전보건교육 ('26.02.25-27)",
                "안전보건협의체 회의 ('26.02.25)",
                "PM 주관 타운홀 미팅 ('26.02.23)",
                "관리감독자 교육 ('26.02.24)",
                "노사합동점검 ('26.02.04)",
                "동절기 어묵 꼬치 나눔 행사 ('26.02.23)",
            ]
        },
        {
            "slide": 8, "category": "해상부", "type": "공정사진",
            "title": "공정사진 (항만공사) - 2월",
            "images_start": 2,
            "captions": [
                "해상부 외부 전경 ('26.02.03)",
                "해상부 외부 전경 ('26.02.03)",
                "벙커링 MD-01 LADDER 설치 ('26.02.02)",
                "LNG BD-01 자켓 청소 ('26.02.02)",
                "LNG MD-01 오일휀스 설치 ('26.02.10)",
                "LNG MD-01 자켓 및 점검로 도장 ('26.02.09)",
            ]
        },
        {
            "slide": 9, "category": "해상부", "type": "안전점검",
            "title": "안전점검 사진 (항만공사) - 2월",
            "images_start": 2,
            "captions": [
                "공사안전보건대장 이행 현황 점검 ('26.02.03)",
                "노사합동점검 ('26.02.10)",
                "중처법 이행현황 월간점검 ('26.02.10)",
                "직책자 임원 점검 ('26.02.11)",
                "위험성평가 사전회의 ('26.02.12)",
                "월간 안전점검 ('26.02.12)",
                "발주자 명절대비 자율점검 ('26.02.12)",
                "작업 재개 전 안전점검 ('26.02.23)",
            ]
        },
        {
            "slide": 10, "category": "154kV", "type": "공정사진",
            "title": "공정사진 (154kV 수전공사) - 2월",
            "images_start": 2,
            "captions": [
                "154kV 수전행사 ('26.02.10)",
                "154kV 수전행사 ('26.02.10)",
                "자동소화장치 설치 ('26.02.04)",
                "접지단자함 명판 교체 ('26.02.04)",
                "자동소화장치 설치 ('26.02.03)",
                "154kV 수전 ('26.02.10)",
            ]
        },
        {
            "slide": 11, "category": "154kV", "type": "안전점검",
            "title": "안전점검 사진 (154kV 수전공사) - 2월",
            "images_start": 2,
            "captions": [
                "주간 특별안전점검 [추락사고 예방] ('26.02.25)",
                "안전보건협의체 ('26.02.12)",
                "발주처 특별안전점검 [시설물 및 정리정돈] ('26.02.20)",
                "순회점검 및 합동안전점검 ('26.02.12)",
                "경영층 특별안전점검 [안전보건실 현장 점검] ('26.02.19)",
                "고위험작업 집중안전관리 ('26.02.01~'26.02.26)",
                "주간 특별안전점검 [구조물] ('26.02.05)",
                "정기안전보건교육 ('26.02.13)",
            ]
        },
    ],
    "03월": [
        {
            "slide": 4, "category": "육상부", "type": "공사사진",
            "title": "공사 사진 (육상부) - 3월",
            "images_start": 3,
            "captions": [
                "#7탱크 잔수 처리 및 청소 ('26.03.20)",
                "#8탱크 Internal Pipe & Support 설치 ('26.03.23)",
                "#7탱크 Roof 도장 ('26.03.20)",
                "LNG 2부두 Jetty 전기실 판넬 설치 ('26.03.28)",
                "제2 LNG터미널 육상부 전경 ('26.03.28)",
                "제2 LNG터미널 해상 Jetty 전경 ('26.03.28)",
            ]
        },
        {
            "slide": 5, "category": "육상부", "type": "안전점검",
            "title": "안전점검 사진 (육상부) - 3월",
            "images_start": 2,
            "captions": [
                "정기안전보건교육 (3.24-3.25)",
                "안전보건협의체 회의 (3.27)",
                "관리감독자교육 (3.20)",
                "그룹사 안전보건경영진단 (3.23~3.24)",
                "신호수 및 유도원 특별교육 (3.10)",
                "자율안전컨설팅 (3.20)",
                "노사합동점검 (3.4)",
                "하반기 안전보건진단 (3.10-3.12)",
            ]
        },
        {
            "slide": 6, "category": "해상부", "type": "공정사진",
            "title": "공정사진 (항만공사) - 3월",
            "images_start": 2,
            "captions": [
                "해상부 외부 전경 ('26.03.04)",
                "해상부 외부 전경 ('26.03.04)",
                "LNG WP 자켓 도장 ('26.03.04)",
                "LNG WP 자켓 도장 ('26.03.12)",
                "제작장 고철용 강관파일 정리 ('26.03.27)",
                "Safety Guard 이설/설치 ('26.03.26)",
            ]
        },
        {
            "slide": 7, "category": "해상부", "type": "안전점검",
            "title": "안전점검 사진 (항만공사) - 3월",
            "images_start": 2,
            "captions": [
                "유해위험기계기구 점검 ('26.03.03)",
                "안전관리계획서 이행현황 점검 ('26.03.04)",
                "해빙기 안전점검 ('26.03.11)",
                "중처법 이행현황 점검 ('26.03.11)",
                "위험성평가 사전회의 ('26.03.11)",
                "현장 안전 타운홀 미팅 ('26.03.11)",
                "산업안전보건위원회 ('26.03.11)",
                "월간 안전점검 ('26.03.19)",
            ]
        },
    ]
}

# Load slides_data.json to resolve image filenames per slide
with open(os.path.join(ROOT, "slides_data.json"), 'r', encoding='utf-8') as f:
    slides_data = json.load(f)

# Build a lookup: month -> slide_num -> images list
slide_lookup = {}
for month, slides in slides_data.items():
    slide_lookup[month] = {s['slide']: s['images'] for s in slides}

# Now build manifest and copy files
os.makedirs(PHOTOS, exist_ok=True)
manifest = {}
for month, pages in PHOTO_PAGES.items():
    month_dir = os.path.join(PHOTOS, month)
    os.makedirs(month_dir, exist_ok=True)
    src_media = os.path.join(EXTRACT, month, "ppt", "media")
    manifest[month] = []
    for page in pages:
        slide_num = page['slide']
        images = slide_lookup[month][slide_num]
        # Get unique images starting from images_start, preserving order
        seen = set()
        photo_files = []
        for img in images[page['images_start']:]:
            if img in seen:
                continue
            seen.add(img)
            photo_files.append(img)
        # Pair with captions (use min length)
        n = min(len(photo_files), len(page['captions']))
        items = []
        for i in range(n):
            fname = photo_files[i]
            caption = page['captions'][i]
            # Copy file with month prefix to avoid collisions
            src = os.path.join(src_media, fname)
            if not os.path.exists(src):
                print(f"WARNING: missing {src}")
                continue
            new_name = f"s{slide_num}_{i+1}_{fname}"
            dst = os.path.join(month_dir, new_name)
            shutil.copy2(src, dst)
            items.append({
                "file": f"photos/{month}/{new_name}",
                "caption": caption,
            })
        manifest[month].append({
            "title": page['title'],
            "category": page['category'],
            "type": page['type'],
            "items": items,
        })
        print(f"{month} - {page['title']}: {len(items)} photos")

with open(os.path.join(ROOT, "photos_manifest.json"), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("\nDONE - manifest at photos_manifest.json")
print(f"Total months: {len(manifest)}")
total = sum(len(item['items']) for pages in manifest.values() for item in pages)
print(f"Total photos copied: {total}")
