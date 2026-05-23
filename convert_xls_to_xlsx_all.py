"""
convert_xls_to_xlsx_all.py — 모든 OLE2(.xls binary) 형식의 월간회의 xlsx 파일을 정상 xlsx로 변환.

OneDrive 부분동기화/구버전 저장 등으로 .xlsx 확장자를 갖지만 내부는 OLE2(.xls)인 파일을
Excel COM 으로 열어 임시 .xls → SaveAs(.xlsx, FileFormat=51) 로 다시 저장.

처리 대상:
- 2024-01 ~ 2024-11 (24년 거의 전부)
- 2025-01, 2025-09, 2025-11
- 2026-02, 2026-04

출력: _xlsx_converted_all/<원본명>.xlsx
"""
import sys
import os
import shutil
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import win32com.client as wc
import pythoncom

ROOT = Path(__file__).parent.resolve()
OUT_DIR = ROOT / "_xlsx_converted_all"
OUT_DIR.mkdir(exist_ok=True)

XL_OPEN_XML = 51

TARGETS = [
    "광)7,8탱크_월간안전공정회의 (24.1월)_Final_R1.xlsx",
    "광)7,8탱크_월간안전공정회의 (24.2월)_Final_R1.xlsx",
    "광)7,8탱크_월간안전공정회의 (24.3월)_Final_R3.xlsx",
    "광)7,8탱크_월간안전공정회의 (24.4월)_Final_R1.xlsx",
    "광)7,8탱크_월간안전공정회의 (24.5월)_Final.xlsx",
    "광)7,8탱크_월간안전공정회의 (24.6월)_Final_R2.xlsx",
    "광)7,8탱크_월간안전공정회의 (24.7월)_Final_R2.xlsx",
    "광)7,8탱크_월간안전공정회의_24.8월_Final.xlsx",
    "광)7,8탱크_월간안전공정회의_24.9월_Final_R1.xlsx",
    "광)7,8탱크_월간안전공정회의_24.10월_Final_R1.xlsx",
    "광)7,8탱크_월간안전공정회의_24.11월_Final.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_25.1월_Final_R3.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_25.9월_Final.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_25.11월_Final.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_26.2월_Final_R1.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_26.4월_Final.xlsx",
]


def is_ole2(p):
    return open(p, "rb").read(8).hex().startswith("d0cf11e0") or not open(p, "rb").read(8).hex().startswith("504b")


def main():
    pythoncom.CoInitialize()
    excel = wc.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.AskToUpdateLinks = False
    try:
        for fname in TARGETS:
            src = ROOT / fname
            if not src.exists():
                print(f"[SKIP] {fname}: 파일 없음")
                continue

            # 헤더 OLE2 면 임시로 .xls 로 복사 후 SaveAs xlsx (Excel 가 새 형식으로 강제 변환)
            head = open(src, "rb").read(8).hex()
            if head.startswith("504b"):
                # 이미 정상 zip xlsx — 복사만
                dst = OUT_DIR / fname
                if not dst.exists():
                    shutil.copy(src, dst)
                print(f"[COPY] {fname} (이미 정상)")
                continue

            tmp_dir = Path(tempfile.mkdtemp(prefix="xls_conv_"))
            tmp_xls = tmp_dir / (src.stem + ".xls")
            shutil.copy(src, tmp_xls)
            try:
                wb = excel.Workbooks.Open(str(tmp_xls), UpdateLinks=0, ReadOnly=True, IgnoreReadOnlyRecommended=True)
                dst = OUT_DIR / fname
                if dst.exists():
                    dst.unlink()
                wb.CheckCompatibility = False
                wb.SaveAs(str(dst), FileFormat=XL_OPEN_XML, ConflictResolution=2)
                wb.Close(SaveChanges=False)
                new_head = open(dst, "rb").read(8).hex()
                ok = new_head.startswith("504b")
                print(f"[{'OK ' if ok else 'XML?'}] {fname} -> head={new_head}")
            except Exception as e:
                print(f"[ERR] {fname}: {e}")
            finally:
                try:
                    if tmp_xls.exists():
                        tmp_xls.unlink()
                    tmp_dir.rmdir()
                except Exception:
                    pass
    finally:
        try:
            excel.Quit()
        except Exception:
            pass
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
