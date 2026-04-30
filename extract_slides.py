# -*- coding: utf-8 -*-
import os
import re
import json
import sys
import xml.etree.ElementTree as ET

# Force stdout to utf-8 on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = r"C:/Users/kyungtae/OneDrive - POSCO INTERNATIONAL/바탕 화면/대시보드/ppt_extract"
MONTHS = ["01월", "02월", "03월"]

# Namespace mapping
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def slide_sort_key(name):
    m = re.match(r'slide(\d+)\.xml$', name)
    return int(m.group(1)) if m else 0


def parse_rels(rels_path):
    """Return dict of rId -> image filename (basename) for image-type rels."""
    mapping = {}
    if not os.path.exists(rels_path):
        return mapping
    try:
        tree = ET.parse(rels_path)
    except ET.ParseError:
        return mapping
    root = tree.getroot()
    # Relationships have no specific ns prefix in a:t style; iterate
    for rel in root.findall('rel:Relationship', NS):
        rid = rel.get('Id')
        target = rel.get('Target', '')
        # Only consider images (path contains "media/")
        if 'media/' in target.replace('\\', '/'):
            basename = os.path.basename(target.replace('\\', '/'))
            mapping[rid] = basename
    return mapping


def parse_slide(slide_path, rels_map):
    """Extract texts (in order) and ordered list of image filenames referenced."""
    tree = ET.parse(slide_path)
    root = tree.getroot()

    texts = []
    images = []

    # Walk in document order to keep text reading order
    for elem in root.iter():
        tag = elem.tag
        # Strip namespace
        if '}' in tag:
            local = tag.split('}', 1)[1]
        else:
            local = tag

        if local == 't':
            # a:t text element
            if elem.text is not None:
                t = elem.text
                if t.strip() != "":
                    texts.append(t)
        elif local == 'blip':
            # a:blip with r:embed attribute
            embed = elem.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if embed and embed in rels_map:
                img = rels_map[embed]
                images.append(img)

    return texts, images


def main():
    result = {}
    for month in MONTHS:
        slides_dir = os.path.join(ROOT, month, 'ppt', 'slides')
        rels_dir = os.path.join(slides_dir, '_rels')
        if not os.path.isdir(slides_dir):
            result[month] = []
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

            month_data.append({
                'slide': num,
                'texts': texts,
                'images': images,
            })
        result[month] = month_data

    out_path = r"C:/Users/kyungtae/OneDrive - POSCO INTERNATIONAL/바탕 화면/대시보드/slides_data.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Print to stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
