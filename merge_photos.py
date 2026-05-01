# -*- coding: utf-8 -*-
"""
1. 기존 photos.js를 파싱하여 PHOTOS_DATA 추출
2. 키 변환: '06월'~'12월' → '2025-06'~'2025-12', '01월'~'03월' → '2026-01'~'2026-03'
3. 사진 폴더 이동: photos/06월/ → photos/2025-06/ (등)
4. 사진 파일 경로도 함께 변경
5. legacy manifest와 병합 → 새 photos.js 생성
"""
import os
import re
import json
import shutil
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\14ZB95N\Desktop\대시보드"
PHOTOS = os.path.join(ROOT, "photos")

# 기존 photos.js → JSON으로 파싱 (window.PHOTOS_DATA = {...};)
with open(os.path.join(ROOT, 'photos.js'), 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'window\.PHOTOS_DATA\s*=\s*(\{.*\});?\s*$', content, re.DOTALL)
if not m:
    print("ERROR: cannot parse photos.js")
    sys.exit(1)
existing_data = json.loads(m.group(1))

# Old key → New key
KEY_MAP = {
    '06월': '2025-06', '07월': '2025-07', '08월': '2025-08', '09월': '2025-09',
    '10월': '2025-10', '11월': '2025-11', '12월': '2025-12',
    '01월': '2026-01', '02월': '2026-02', '03월': '2026-03',
}

# 1. 폴더 이동
for old, new in KEY_MAP.items():
    old_dir = os.path.join(PHOTOS, old)
    new_dir = os.path.join(PHOTOS, new)
    if os.path.exists(old_dir) and not os.path.exists(new_dir):
        shutil.move(old_dir, new_dir)
        print(f"  moved: {old} → {new}")
    elif os.path.exists(old_dir):
        # 둘 다 있으면 병합 (덮어쓰지 않음)
        for f in os.listdir(old_dir):
            src = os.path.join(old_dir, f)
            dst = os.path.join(new_dir, f)
            if not os.path.exists(dst):
                shutil.move(src, dst)
        try:
            os.rmdir(old_dir)
        except OSError:
            pass

# 2. 데이터 키 변환 + file 경로 변환
new_data = {}
for old_key, sections in existing_data.items():
    new_key = KEY_MAP.get(old_key, old_key)
    new_sections = []
    for sec in sections:
        new_items = []
        for it in sec['items']:
            new_file = it['file'].replace(f'photos/{old_key}/', f'photos/{new_key}/')
            new_items.append({**it, 'file': new_file})
        new_sections.append({**sec, 'items': new_items})
    new_data[new_key] = new_sections

# 3. legacy manifest 병합
with open(os.path.join(ROOT, 'photos_manifest_legacy.json'), 'r', encoding='utf-8') as f:
    legacy = json.load(f)

for key, sections in legacy.items():
    if key in new_data:
        new_data[key].extend(sections)
    else:
        new_data[key] = sections

# 4. 키 정렬 (YYYY-MM)
sorted_data = {}
for k in sorted(new_data.keys()):
    sorted_data[k] = new_data[k]

# 5. 새 photos.js 작성
out = "window.PHOTOS_DATA = " + json.dumps(sorted_data, ensure_ascii=False, indent=2) + ";\n"
with open(os.path.join(ROOT, 'photos.js'), 'w', encoding='utf-8') as f:
    f.write(out)

# 통계
total = sum(len(it) for sections in sorted_data.values() for sec in sections for it in [sec['items']])
total_items = sum(len(sec['items']) for sections in sorted_data.values() for sec in sections)
print(f"\n[DONE]")
print(f"Months: {len(sorted_data)}")
print(f"Total photos: {total_items}")
for k in sorted(sorted_data.keys()):
    n = sum(len(sec['items']) for sec in sorted_data[k])
    print(f"  {k}: {len(sorted_data[k])} sections, {n} photos")
