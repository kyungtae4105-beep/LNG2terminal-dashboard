"""
convert_xls_to_xlsx2.py — 2차 변환 시도

1차에서 SaveAs FileFormat=51 으로 .xlsx 확장자로 저장했지만
내부는 여전히 OLE2(.xls binary) 인 파일들이 있음.
이번엔 변환된 파일을 한 번 더 열어서 강제로 xlOpenXMLWorkbook 으로 재저장.
"""
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import win32com.client as wc
import pythoncom

ROOT = Path(__file__).parent.resolve()
IN_DIR = ROOT / "_xlsx_converted"
OUT_DIR = ROOT / "_xlsx_converted2"
OUT_DIR.mkdir(exist_ok=True)

XL_OPEN_XML = 51

def main():
    pythoncom.CoInitialize()
    excel = wc.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.AskToUpdateLinks = False
    try:
        for src in IN_DIR.glob("*.xlsx"):
            head = open(src, "rb").read(8).hex()
            if head.startswith("504b"):
                # 이미 정상 ZIP 헤더
                dst = OUT_DIR / src.name
                dst.write_bytes(src.read_bytes())
                print(f"[COPY] {src.name} (이미 정상)")
                continue
            try:
                wb = excel.Workbooks.Open(str(src), UpdateLinks=0, ReadOnly=True, IgnoreReadOnlyRecommended=True)
                # Excel 호환 모드 강제 해제 + FileFormat=51 명시
                dst = OUT_DIR / src.name
                wb.CheckCompatibility = False
                wb.SaveAs(str(dst), FileFormat=XL_OPEN_XML, ConflictResolution=2)
                wb.Close(SaveChanges=False)
                new_head = open(dst, "rb").read(8).hex()
                ok = new_head.startswith("504b")
                print(f"[{'OK ' if ok else 'XML?'}] {src.name} -> head={new_head}")
            except Exception as e:
                print(f"[ERR] {src.name}: {e}")
    finally:
        try:
            excel.Quit()
        except Exception:
            pass
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
