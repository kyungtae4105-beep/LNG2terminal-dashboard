# -*- coding: utf-8 -*-
"""
2023/2024년 광양 LNG터미널 PPTX 파일을 일괄 추출하여
- ppt_extract_legacy/{YYYY-MM}/ : zip 풀린 PPT 구조
- slides_data_legacy.json       : 슬라이드별 텍스트/이미지 매핑

기존 2025/2026 데이터는 건드리지 않는다.
"""
import os
import re
import sys
import json
import zipfile
import shutil
import xml.etree.ElementTree as ET

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = r"C:\Users\14ZB95N\Desktop\대시보드"
EXTRACT_BASE = os.path.join(ROOT, "ppt_extract_legacy")
OUT_JSON = os.path.join(ROOT, "slides_data_legacy.json")

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


# 파일명 → (연도, 월) 매핑
def parse_file(name):
    """
    Examples:
      터미널건설추진반_2023년 광양 LNG터미널 증설공사 건설실적(12월)_...
      터미널건설추진반_광양 LNG 터미널 증설공사 월간 업무보고(23.05월 실적)_...
      터미널건설추진반_광양 LNG 터미널 증설공사 월간 업무보고(23년2월)_...
      터미널건설추진반_2024년 광양 LNG터미널 증설공사 건설실적(10월)_...
    """
    base = os.path.basename(name)
    # 연도 추출
    m = re.search(r'(20\d{2})년', base)
    if m:
        year = int(m.group(1))
    else:
        m = re.search(r"\((\d{2})[\.년]", base)
        if m:
            year = 2000 + int(m.group(1))
        else:
            return None
    # 월 추출: ( ... XX월 ... )
    mm = re.search(r'(\d{1,2})\s*월', base)
    if not mm:
        return None
    month = int(mm.group(1))
    if month < 1 or month > 12:
        return None
    # "사본" 파일은 스킵
    if "사본" in base:
        return None
    return year, month


def slide_sort_key(name):
    m = re.match(r'slide(\d+)\.xml$', name)
    return int(m.group(1)) if m else 0


def parse_rels(rels_path):
    mapping = {}
    if not os.path.exists(rels_path):
        return mapping
    try:
        tree = ET.parse(rels_path)
    except ET.ParseError:
        return mapping
    root = tree.getroot()
    for rel in root.findall('rel:Relationship', NS):
        rid = rel.get('Id')
        target = rel.get('Target', '')
        if 'media/' in target.replace('\\', '/'):
            basename = os.path.basename(target.replace('\\', '/'))
            mapping[rid] = basename
    return mapping


def parse_slide(slide_path, rels_map):
    tree = ET.parse(slide_path)
    root = tree.getroot()
    texts = []
    images = []
    for elem in root.iter():
        tag = elem.tag
        local = tag.split('}', 1)[1] if '}' in tag else tag
        if local == 't':
            if elem.text and elem.text.strip():
                texts.append(elem.text)
        elif local == 'blip':
            embed = elem.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if embed and embed in rels_map:
                images.append(rels_map[embed])
    return texts, images


def main():
    pptx_files = []
    for fn in os.listdir(ROOT):
        if not fn.lower().endswith('.pptx'):
            continue
        if not fn.startswith("터미널건설추진반"):
            continue  # 과제정의서 등 제외
        pinfo = parse_file(fn)
        if pinfo:
            year, month = pinfo
            # 2023/2024만 처리
            if year in (2023, 2024):
                pptx_files.append((year, month, fn))
    pptx_files.sort()

    print(f"[INFO] Total {len(pptx_files)} legacy PPTX to process")
    for y, m, fn in pptx_files:
        print(f"  {y}-{m:02d}: {fn}")

    if os.path.exists(EXTRACT_BASE):
        shutil.rmtree(EXTRACT_BASE)
    os.makedirs(EXTRACT_BASE, exist_ok=True)

    result = {}
    for year, month, fn in pptx_files:
        key = f"{year}-{month:02d}"
        target_dir = os.path.join(EXTRACT_BASE, key)
        os.makedirs(target_dir, exist_ok=True)
        src = os.path.join(ROOT, fn)
        try:
            with zipfile.ZipFile(src, 'r') as z:
                z.extractall(target_dir)
        except Exception as e:
            print(f"[WARN] {key} extract failed: {e}")
            continue

        slides_dir = os.path.join(target_dir, 'ppt', 'slides')
        rels_dir = os.path.join(slides_dir, '_rels')
        if not os.path.isdir(slides_dir):
            print(f"[WARN] {key}: no slides dir")
            result[key] = []
            continue

        slide_files = [f for f in os.listdir(slides_dir) if re.match(r'slide\d+\.xml$', f)]
        slide_files.sort(key=slide_sort_key)
        month_data = []
        for sf in slide_files:
            num = slide_sort_key(sf)
            slide_path = os.path.join(slides_dir, sf)
            rels_path = os.path.join(rels_dir, sf + '.rels')
            rels_map = parse_rels(rels_path)
            texts, images = parse_slide(slide_path, rels_map)
            month_data.append({'slide': num, 'texts': texts, 'images': images})
        result[key] = month_data
        print(f"[OK] {key}: {len(month_data)} slides extracted")

    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Saved {OUT_JSON}")


if __name__ == '__main__':
    main()
