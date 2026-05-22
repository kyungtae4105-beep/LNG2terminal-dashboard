"""
convert_xls_to_xlsx.py

OneDrive 부분동기화로 OLE2(.xls) 헤더로 저장된 .xlsx 파일들을
Excel COM 으로 열어서 정상 .xlsx 로 다시 저장한다.

대상:
- 25.9월, 25.11월, 26.2월 (.xls OLE2 형식)
- 26.3월, 26.4월 (현재 다른 프로세스가 열고 있을 수 있음)

변환 결과는 _xlsx/ 하위 디렉토리에 저장 (원본 보존).
"""
import os
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
OUT_DIR = ROOT / "_xlsx_converted"
OUT_DIR.mkdir(exist_ok=True)

# xlOpenXMLWorkbook = 51
XL_OPEN_XML = 51

TARGETS = [
    "광)LNG #7,8탱크_월간안전공정회의_25.9월_Final.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_25.11월_Final.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_26.2월_Final_R1.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_26.3월_Final.xlsx",
    "광)LNG #7,8탱크_월간안전공정회의_26.4월_Final.xlsx",
]


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
            dst = OUT_DIR / fname  # 동일 이름, 확장자 유지
            try:
                wb = excel.Workbooks.Open(str(src), UpdateLinks=0, ReadOnly=True)
                # SaveAs XLSX
                wb.SaveAs(str(dst), FileFormat=XL_OPEN_XML)
                wb.Close(SaveChanges=False)
                print(f"[OK ] {fname} -> {dst.name}")
            except Exception as e:
                print(f"[ERR] {fname}: {e}")
    finally:
        try:
            excel.Quit()
        except Exception:
            pass
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
