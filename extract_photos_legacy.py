# -*- coding: utf-8 -*-
"""
2023-2024년 PPTX의 사진을 위치(좌표) 기반으로 캡션과 정밀 매칭.

각 슬라이드 XML에서:
  - <p:sp> (텍스트 박스): off(x, y) + ext(cx, cy) → 텍스트 영역
  - <p:pic> (이미지)    : off(x, y) + ext(cx, cy) → 이미지 영역

이미지마다 가장 "그럴듯한" 캡션을 찾기:
  - 후보: 이미지 박스의 바로 아래 / 중앙 X 가까운 텍스트 박스
  - 우선순위: (1) Y 거리 (이미지 아래쪽이고 가까운 것), (2) X 중앙 거리

결과: photos_manifest_legacy.json + photos/{YYYY-MM}/ 디렉토리
"""
import os
import re
import sys
import json
import shutil
import xml.etree.ElementTree as ET

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = r"C:\Users\14ZB95N\Desktop\대시보드"
EXTRACT_BASE = os.path.join(ROOT, "ppt_extract_legacy")
PHOTOS = os.path.join(ROOT, "photos")
OUT_JSON = os.path.join(ROOT, "photos_manifest_legacy.json")

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


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


def get_xfrm(elem):
    """Return (x, y, cx, cy) in EMU, or None."""
    # search for a:xfrm or p:xfrm
    xfrm = None
    for child in elem.iter():
        ltag = child.tag.split('}', 1)[1] if '}' in child.tag else child.tag
        if ltag == 'xfrm':
            xfrm = child
            break
    if xfrm is None:
        return None
    off = None
    ext = None
    for c in list(xfrm):
        ltag = c.tag.split('}', 1)[1] if '}' in c.tag else c.tag
        if ltag == 'off':
            off = c
        elif ltag == 'ext':
            ext = c
    if off is None or ext is None:
        return None
    try:
        x = int(off.get('x', 0))
        y = int(off.get('y', 0))
        cx = int(ext.get('cx', 0))
        cy = int(ext.get('cy', 0))
    except (TypeError, ValueError):
        return None
    return (x, y, cx, cy)


def collect_text(sp_elem):
    """Collect <a:t> text inside a shape, joined."""
    parts = []
    for t in sp_elem.iter():
        ltag = t.tag.split('}', 1)[1] if '}' in t.tag else t.tag
        if ltag == 't' and t.text:
            parts.append(t.text)
    # 한 텍스트 박스 내 여러 t 요소를 그대로 이어 붙임
    return ''.join(parts).strip()


def parse_slide(slide_path, rels_map):
    """
    Returns:
      shapes: [{type:'sp'|'pic', x, y, cx, cy, text or imgfile}]
    """
    tree = ET.parse(slide_path)
    root = tree.getroot()
    shapes = []
    # spTree 자식들만 순회
    sp_tree = None
    for el in root.iter():
        ltag = el.tag.split('}', 1)[1] if '}' in el.tag else el.tag
        if ltag == 'spTree':
            sp_tree = el
            break
    if sp_tree is None:
        return shapes

    for child in list(sp_tree):
        ltag = child.tag.split('}', 1)[1] if '}' in child.tag else child.tag
        if ltag == 'sp':
            xfrm = get_xfrm(child)
            if xfrm is None:
                continue
            x, y, cx, cy = xfrm
            text = collect_text(child)
            if text:
                shapes.append({'type': 'sp', 'x': x, 'y': y, 'cx': cx, 'cy': cy, 'text': text})
        elif ltag == 'pic':
            xfrm = get_xfrm(child)
            if xfrm is None:
                continue
            x, y, cx, cy = xfrm
            # 이미지 파일 찾기
            imgfile = None
            for blip in child.iter():
                bltag = blip.tag.split('}', 1)[1] if '}' in blip.tag else blip.tag
                if bltag == 'blip':
                    embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if embed and embed in rels_map:
                        imgfile = rels_map[embed]
                        break
            if imgfile:
                shapes.append({'type': 'pic', 'x': x, 'y': y, 'cx': cx, 'cy': cy, 'imgfile': imgfile})
        elif ltag == 'grpSp':
            # grouped shapes: recurse but treat at top level
            for grand in list(child):
                gtag = grand.tag.split('}', 1)[1] if '}' in grand.tag else grand.tag
                if gtag == 'sp':
                    xfrm = get_xfrm(grand)
                    if xfrm is None:
                        continue
                    x, y, cx, cy = xfrm
                    text = collect_text(grand)
                    if text:
                        shapes.append({'type': 'sp', 'x': x, 'y': y, 'cx': cx, 'cy': cy, 'text': text})
                elif gtag == 'pic':
                    xfrm = get_xfrm(grand)
                    if xfrm is None:
                        continue
                    x, y, cx, cy = xfrm
                    imgfile = None
                    for blip in grand.iter():
                        bltag = blip.tag.split('}', 1)[1] if '}' in blip.tag else blip.tag
                        if bltag == 'blip':
                            embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                            if embed and embed in rels_map:
                                imgfile = rels_map[embed]
                                break
                    if imgfile:
                        shapes.append({'type': 'pic', 'x': x, 'y': y, 'cx': cx, 'cy': cy, 'imgfile': imgfile})
    return shapes


def has_date_pattern(text):
    """캡션 일자 패턴 (YY.MM.DD)가 텍스트에 있는지."""
    # ('23.02.28), ('23.2.10) 등 다양
    return bool(re.search(r"['‘’]?\s*\d{2}[\.\-]\s*\d{1,2}[\.\-]\s*\d{1,2}", text))


def is_caption_like(text):
    """캡션으로 보이는 짧은 한국어 + 날짜형 텍스트."""
    if len(text) > 200:
        return False
    s = text.strip()
    # 헤더/표지 패턴 제외
    if re.match(r'^[■○●▣▶]', s):
        return False
    if re.match(r'^\d+\.\s', s):  # "1. 안전관리..." 등 항목번호
        return False
    if '기준' in s and len(s) < 25:  # "'24.01.31 기준"
        return False
    if re.match(r'^(공정\s*사진|안전점검\s*사진|공사\s*사진|항만공사\s*사진|현장전경)', s):
        # 섹션 타이틀 자체는 캡션 아님
        return False
    if has_date_pattern(text):
        return True
    if len(s) < 60 and any(ch in s for ch in ['공사', '점검', '교육', '훈련', '설치', '타설', '전경', '회의', '용접', '시공', '굴착', '항타', '도장', '보수']):
        return True
    return False


def is_section_title(text):
    """섹션 타이틀 패턴 ('공정 사진', '안전점검 사진', '공사 사진' 등)."""
    s = text.strip()
    if len(s) > 30:
        return False
    return bool(re.match(r'^(공정\s*사진|안전점검\s*사진|공사\s*사진|항만공사\s*사진|현장전경)', s))


def emu_to_norm(v, max_v):
    """EMU를 0~1로 정규화 (단순)."""
    return v / max_v if max_v else 0


def cluster_texts_for_image(pic, txts, max_dx=2500000, search_y_below=2500000):
    """이미지 주변(주로 아래)의 텍스트 박스를 모아 한 캡션으로 합침.
    - max_dx: 가로방향 허용 범위 (~25mm)
    - search_y_below: 이미지 하단으로부터 search 범위
    """
    pic_left = pic['x']
    pic_right = pic['x'] + pic['cx']
    pic_bottom = pic['y'] + pic['cy']

    nearby = []
    for t in txts:
        if t.get('used'):
            continue
        # X 겹침 또는 가까움
        t_cx = t['x'] + t['cx'] // 2
        # 텍스트 박스가 이미지 X 범위와 겹치는지 / 가까운지
        x_overlap = not (t['x'] + t['cx'] < pic_left - max_dx or t['x'] > pic_right + max_dx)
        if not x_overlap:
            continue
        # Y 위치: 이미지 아래 search_y_below 이내
        if t['y'] < pic_bottom - 200000:  # 이미지보다 위쪽
            continue
        if t['y'] > pic_bottom + search_y_below:
            continue
        nearby.append(t)

    if not nearby:
        return None, []

    # Y, X 순으로 정렬
    nearby.sort(key=lambda t: (t['y'], t['x']))

    # 캡션 fragment 합치기: 가장 위(Y) 텍스트 박스부터 차례로
    # 단, 이미지의 X 중앙선과 너무 떨어진 박스는 제외
    pic_cx_x = pic['x'] + pic['cx'] // 2
    selected = []
    for t in nearby:
        t_cx = t['x'] + t['cx'] // 2
        # X 중앙 거리가 이미지 폭의 0.7배 이내
        if abs(t_cx - pic_cx_x) < pic['cx'] * 0.8 + 200000:
            selected.append(t)
        if len(selected) >= 8:  # too many fragments
            break

    if not selected:
        return None, []

    # Y 좌표가 비슷한 박스끼리 묶어 한 줄로 합치기
    text_combined = ' '.join(t['text'] for t in selected)
    # 다중 공백 정리
    text_combined = re.sub(r'\s+', ' ', text_combined).strip()

    return text_combined, selected


def assign_captions(shapes):
    """
    각 이미지에게 캡션 텍스트 박스 매칭.
    1. 단일 캡션 매칭(기존 로직): X 중앙 + Y 거리 기반 가장 가까운 미할당 캡션
    2. 단일 매칭 실패 시 클러스터링: 이미지 주변 fragment 들을 합쳐 캡션 만듦
    """
    pics = [s for s in shapes if s['type'] == 'pic']
    txts = [s for s in shapes if s['type'] == 'sp']

    # 각 텍스트가 단일 캡션 후보인지 먼저 분류
    candidates = []
    for t in txts:
        text = t['text']
        if is_caption_like(text):
            candidates.append({**t, 'used': False, 'kind': 'caption'})

    # 단일 매칭에 사용되지 않은 텍스트 박스도 클러스터링 후보로 보존
    all_txts = [{**t, 'used': False} for t in txts]

    pics_sorted = sorted(pics, key=lambda p: (p['y'], p['x']))

    results = []
    for pic in pics_sorted:
        pic_cx_x = pic['x'] + pic['cx'] // 2
        pic_bottom_y = pic['y'] + pic['cy']

        best = None
        best_score = float('inf')
        for c in candidates:
            if c['used']:
                continue
            cap_cx_x = c['x'] + c['cx'] // 2
            cap_top_y = c['y']
            dx = abs(cap_cx_x - pic_cx_x)
            dy = cap_top_y - pic_bottom_y
            if dy < -pic['cy'] // 2:
                continue
            score = dx + max(0, dy) * 1.5 + max(0, -dy) * 0.8
            if score < best_score:
                best_score = score
                best = c

        caption = ''
        if best is not None and best_score < 4000000:  # 4cm 이내 합리적
            best['used'] = True
            caption = best['text']
            # 사용된 텍스트 박스를 all_txts에서도 used 처리
            for at in all_txts:
                if at['x'] == best['x'] and at['y'] == best['y'] and at['text'] == best['text']:
                    at['used'] = True
                    break

        if not caption:
            # Fallback: 클러스터링으로 fragment 합치기
            cluster_caption, used_txts = cluster_texts_for_image(pic, all_txts)
            if cluster_caption and len(cluster_caption) >= 5:
                # 사용한 텍스트 박스 marking
                for ut in used_txts:
                    for at in all_txts:
                        if at['x'] == ut['x'] and at['y'] == ut['y'] and at['text'] == ut['text']:
                            at['used'] = True
                            break
                caption = cluster_caption

        results.append({
            'imgfile': pic['imgfile'],
            'x': pic['x'], 'y': pic['y'],
            'caption': caption,
        })

    return results


def find_section_title(shapes):
    """슬라이드의 메인 섹션 타이틀 찾기."""
    # 슬라이드 상단(Y < 1500000 ~ 약 1.5cm)이고 폭이 넓은 텍스트 박스 우선
    candidates = []
    for s in shapes:
        if s['type'] != 'sp':
            continue
        if is_section_title(s['text']):
            candidates.append(s)
    if not candidates:
        # fallback
        for s in shapes:
            if s['type'] != 'sp':
                continue
            text = s['text']
            if any(kw in text for kw in ['공정사진', '안전점검 사진', '공사 사진', '항만공사', '현장전경', '공정 사진', '안전점검']):
                candidates.append(s)
    if not candidates:
        return ''
    candidates.sort(key=lambda c: (c['y'], -c['cx']))
    return candidates[0]['text'].strip()


def categorize(title):
    """타이틀에서 카테고리/유형 추출."""
    t = title or ''
    # 카테고리
    if '항만' in t or '해상' in t:
        category = '해상부'
    elif '#6' in t or '#7' in t or '#8' in t or '탱크' in t or '육상' in t:
        category = '육상부'
    else:
        category = '육상부'  # default
    # 유형
    if '안전점검' in t or '안전' in t:
        type_ = '안전점검'
    elif '공정사진' in t or '공정 사진' in t or '공사' in t:
        type_ = '공정사진'
    else:
        type_ = '공정사진'
    return category, type_


def main():
    # slides_data_legacy.json 로드 (보조)
    with open(os.path.join(ROOT, 'slides_data_legacy.json'), 'r', encoding='utf-8') as f:
        slides_data = json.load(f)

    manifest = {}
    for key in sorted(slides_data.keys()):  # YYYY-MM
        slide_dir = os.path.join(EXTRACT_BASE, key, 'ppt', 'slides')
        rels_dir = os.path.join(slide_dir, '_rels')
        media_dir = os.path.join(EXTRACT_BASE, key, 'ppt', 'media')

        if not os.path.isdir(slide_dir):
            continue

        out_dir = os.path.join(PHOTOS, key)
        os.makedirs(out_dir, exist_ok=True)

        manifest[key] = []
        slide_files = sorted([f for f in os.listdir(slide_dir) if re.match(r'slide\d+\.xml$', f)],
                              key=lambda n: int(re.search(r'\d+', n).group()))

        for sf in slide_files:
            num = int(re.search(r'\d+', sf).group())
            slide_path = os.path.join(slide_dir, sf)
            rels_path = os.path.join(rels_dir, sf + '.rels')
            rels_map = parse_rels(rels_path)
            shapes = parse_slide(slide_path, rels_map)

            pics = [s for s in shapes if s['type'] == 'pic']
            if len(pics) < 4:
                continue

            # slide 1, 2는 표지/공정률표/안전관리표 페이지 → 항상 제외
            if num <= 2:
                continue

            # 안전관리표 페이지 검출: 한 텍스트 박스 안에 카테고리 5개 이상 → 표 헤더
            safety_keywords = ['추락', '전도', '낙하', '비래', '감전', '협착', '붕괴', '도괴', '화재', '폭발', '질식']
            is_safety_table = False
            for sp in shapes:
                if sp['type'] != 'sp':
                    continue
                count = sum(1 for kw in safety_keywords if kw in sp['text'])
                if count >= 5:
                    is_safety_table = True
                    break
            if is_safety_table:
                continue
            # 공정률 표 페이지 검출
            all_text = ' '.join(s['text'] for s in shapes if s['type'] == 'sp')
            if all(kw in all_text for kw in ['공정률', '토목', '기계', '전기']) and '계획' in all_text and '실적' in all_text:
                continue
            # Near Miss 페이지 검출
            if 'Near Miss' in all_text or '재해 유형' in all_text and '발생경위' in all_text:
                continue

            title = find_section_title(shapes)

            # 캡션 매칭
            assigned = assign_captions(shapes)

            # 캡션이 헤더성("■", "○", "3. ..." 등)이면 제거 (강한 필터)
            valid_items = []
            for a in assigned:
                cap = a['caption'].strip()
                if not cap:
                    continue
                # 매우 짧은 캡션 (3글자 이하) 제외
                if len(cap) < 4:
                    continue
                # 단순 섹션 타이틀이면 제외
                if re.match(r'^(공정\s*사진|안전점검\s*사진|공사\s*사진|항만공사\s*사진|현장전경)', cap):
                    continue
                valid_items.append(a)

            if len(valid_items) < 2:
                continue

            category, type_ = categorize(title)

            # 사진 복사 + manifest 항목 생성
            section_items = []
            seen = set()
            for i, item in enumerate(valid_items):
                fname = item['imgfile']
                if fname in seen:
                    continue
                seen.add(fname)
                src = os.path.join(media_dir, fname)
                if not os.path.exists(src):
                    continue
                # 파일 확장자 유지
                new_name = f's{num}_{i+1}_{fname}'
                dst = os.path.join(out_dir, new_name)
                shutil.copy2(src, dst)
                # 캡션 정리
                cap = item['caption'].strip()
                # 너무 긴 캡션 trim
                if len(cap) > 120:
                    cap = cap[:120] + '...'
                section_items.append({
                    'file': f'photos/{key}/{new_name}',
                    'caption': cap,
                })

            if section_items:
                # 월 라벨링 추가
                month_label = f"({int(key.split('-')[1])}월)"
                full_title = f"{title} - {key.split('-')[0]}.{int(key.split('-')[1]):02d}월"
                manifest[key].append({
                    'title': full_title,
                    'category': category,
                    'type': type_,
                    'items': section_items,
                    'slide': num,
                })

        n_photos = sum(len(s['items']) for s in manifest[key])
        print(f"[{key}] {len(manifest[key])} sections, {n_photos} photos")

    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] {OUT_JSON}")
    total = sum(len(s['items']) for sections in manifest.values() for s in sections)
    print(f"Total photos: {total} across {len(manifest)} months")


if __name__ == '__main__':
    main()
