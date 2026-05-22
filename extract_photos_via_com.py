"""
extract_photos_via_com.py

OLE2(.xls 헤더) 로 저장된 엑셀 파일에서
11.공사사진대장 시트의 임베디드 이미지+캡션을 Excel COM 으로 직접 추출.
openpyxl 우회.

대상 월: 25.9, 25.11, 26.2, 26.3 (이미 추출된 다른 월은 skip)
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import win32com.client as wc
import pythoncom

ROOT = Path(__file__).parent.resolve()
PHOTOS_DIR = ROOT / "photos"
PHOTOS_JS = ROOT / "photos.js"

TARGETS = [
    ("2025-09", "광)LNG #7,8탱크_월간안전공정회의_25.9월_Final.xlsx"),
    ("2025-11", "광)LNG #7,8탱크_월간안전공정회의_25.11월_Final.xlsx"),
    ("2026-02", "광)LNG #7,8탱크_월간안전공정회의_26.2월_Final_R1.xlsx"),
    ("2026-03", "광)LNG #7,8탱크_월간안전공정회의_26.3월_Final.xlsx"),
]

# xlPicture = 13
# xlBitmap = 2
XL_PICTURE = -4147  # msoPicture (just for filter; we use Shape.Type)
MSO_PICTURE = 13
MSO_LINKEDPICTURE = 11


def find_discipline(row_1idx, headers):
    cur = None
    for hr, hn in headers:
        if hr <= row_1idx:
            cur = hn
    return cur or "기타"


def detect_headers_from_com(ws):
    """B열에서 카테고리 헤더 검출 (Excel COM)"""
    headers = []
    used_rows = ws.UsedRange.Rows.Count
    for r in range(1, min(used_rows + 1, 200)):
        cell = ws.Cells(r, 2)
        val = cell.Value
        if not val or not isinstance(val, str):
            continue
        s = val.strip().replace(" ", "")
        if s in ("토목", "건축", "기계", "전기"):
            headers.append((r, s))
    return headers


def load_photos_data():
    text = PHOTOS_JS.read_text(encoding="utf-8")
    text = re.sub(r"^\s*window\.PHOTOS_DATA\s*=\s*", "", text, count=1)
    text = text.rstrip().rstrip(";")
    return json.loads(text)


def save_photos_data(data):
    js = "window.PHOTOS_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    PHOTOS_JS.write_text(js, encoding="utf-8")


def main():
    pythoncom.CoInitialize()
    excel = wc.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.AskToUpdateLinks = False
    excel.ScreenUpdating = False

    photos = load_photos_data()
    added_total = 0

    try:
        for ym, fname in TARGETS:
            path = ROOT / fname
            if not path.exists():
                print(f"[SKIP] {ym}: 파일 없음")
                continue
            target_dir = PHOTOS_DIR / ym
            target_dir.mkdir(parents=True, exist_ok=True)
            existing_captions = set()
            if ym in photos:
                for sec in photos[ym]:
                    for it in sec.get("items") or []:
                        cap = (it.get("caption") or "").strip()
                        if cap:
                            existing_captions.add(cap)

            try:
                wb = excel.Workbooks.Open(str(path), UpdateLinks=0, ReadOnly=True)
            except Exception as e:
                print(f"[ERR] {ym}: 워크북 오픈 실패 - {e}")
                continue

            try:
                # 11.공사사진대장 시트 찾기
                target_sheet = None
                for ws in wb.Worksheets:
                    if "공사사진대장" in ws.Name:
                        target_sheet = ws
                        break
                if target_sheet is None:
                    print(f"[SKIP] {ym}: 11.공사사진대장 시트 없음")
                    wb.Close(SaveChanges=False)
                    continue

                headers = detect_headers_from_com(target_sheet)
                # Shapes (이미지) 순회
                shapes = target_sheet.Shapes
                count_shapes = shapes.Count
                per_disc_items = {"토목": [], "건축": [], "기계": [], "전기": [], "기타": []}
                added_for_month = 0
                for i in range(1, count_shapes + 1):
                    try:
                        shp = shapes.Item(i)
                        if shp.Type not in (MSO_PICTURE, MSO_LINKEDPICTURE):
                            continue
                        tl = shp.TopLeftCell  # anchor cell
                        anc_row = tl.Row       # 1-indexed
                        anc_col = tl.Column
                        # 캡션: 13행 아래 셀
                        caption_row = anc_row + 12
                        caption_cell = target_sheet.Cells(caption_row, anc_col + 1)
                        cap_val = caption_cell.Value
                        # 캡션이 없으면 ±1 행 검색
                        if not (cap_val and isinstance(cap_val, str) and len(cap_val.strip()) > 5):
                            for dr in (-1, 1, 11, 13):
                                c = target_sheet.Cells(anc_row + dr, anc_col + 1).Value
                                if c and isinstance(c, str) and len(c.strip()) > 5:
                                    cap_val = c
                                    break
                        if not cap_val or not isinstance(cap_val, str):
                            continue
                        caption = cap_val.strip()
                        if caption in existing_captions:
                            continue
                        # Excel Shape 을 임시 파일로 export — Shape.Copy + Workbook 임시 시트에 paste 후 SaveAs 는 복잡.
                        # 대신 Excel 의 CopyPicture + Chart 객체 활용
                        # 가장 직접적: 임시 워크북에 Chart 만들어서 Shape 붙여넣고 Export
                        tmp_path = ROOT / "_tmp_img.png"
                        try:
                            # ChartObjects.Add(Left, Top, Width, Height) — 시트에 임시 차트
                            ch_obj = target_sheet.ChartObjects().Add(0, 0, shp.Width, shp.Height)
                            ch = ch_obj.Chart
                            shp.Copy()
                            time.sleep(0.05)
                            ch.Paste()
                            ch.Export(str(tmp_path), "PNG")
                            ch_obj.Delete()
                        except Exception as e:
                            print(f"  [WARN] {ym} 이미지 export 실패 (shape #{i}): {e}")
                            try: ch_obj.Delete()
                            except Exception: pass
                            continue
                        if not tmp_path.exists():
                            continue
                        data = tmp_path.read_bytes()
                        tmp_path.unlink()
                        if not data:
                            continue
                        h = hashlib.sha1(data).hexdigest()[:12]
                        disc = find_discipline(anc_row, headers)
                        fname_out = f"cnstr_{disc}_{h}.png"
                        out_path = target_dir / fname_out
                        if not out_path.exists():
                            out_path.write_bytes(data)
                        rel = f"photos/{ym}/{fname_out}"
                        per_disc_items[disc].append({"file": rel, "caption": caption})
                        existing_captions.add(caption)
                        added_for_month += 1
                    except Exception as e:
                        print(f"  [ERR] {ym} shape #{i}: {e}")
                        continue

                # photos.js 에 병합
                if added_for_month > 0:
                    if ym not in photos:
                        photos[ym] = []
                    for disc, items in per_disc_items.items():
                        if not items: continue
                        ym_lbl = ym.replace("-", ".")
                        section_title = f"공사 사진 ({disc}) — {ym_lbl}"
                        target_sec = None
                        for sec in photos[ym]:
                            if (sec.get("title") == section_title and sec.get("type") == "공사사진"):
                                target_sec = sec
                                break
                        if not target_sec:
                            target_sec = {
                                "title": section_title,
                                "category": "육상부",
                                "type": "공사사진",
                                "items": [],
                                "slide": 11,
                            }
                            photos[ym].append(target_sec)
                        target_sec["items"].extend(items)

                print(f"[OK ] {ym}: +{added_for_month} (shapes={count_shapes})")
                added_total += added_for_month

                wb.Close(SaveChanges=False)
            except Exception as e:
                print(f"[ERR] {ym}: {e}")
                try: wb.Close(SaveChanges=False)
                except Exception: pass
    finally:
        try:
            excel.Quit()
        except Exception:
            pass
        pythoncom.CoUninitialize()

    save_photos_data(photos)
    print(f"\n=== 완료: 총 {added_total} 장 추가 ===")


if __name__ == "__main__":
    main()
