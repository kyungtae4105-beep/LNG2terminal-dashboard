#!/usr/bin/env python3
"""
Parse legacy_slide_dump.txt and extract structured data per month.
"""
import re
import json
from pathlib import Path

DUMP = Path(r"C:\Users\14ZB95N\Desktop\대시보드\legacy_slide_dump.txt")
OUT = Path(r"C:\Users\14ZB95N\Desktop\대시보드\legacy_kpi_extracted.json")

with open(DUMP, "r", encoding="utf-8") as f:
    text = f.read()

month_pattern = re.compile(r"^=== (\d{4}-\d{2}) \(\d+ slides\) ===$", re.M)
slide_pattern = re.compile(r"^--- slide (\d+) \(imgs=(\d+)\) ---$", re.M)

month_matches = list(month_pattern.finditer(text))

months = {}
for i, m in enumerate(month_matches):
    month = m.group(1)
    start = m.end()
    end = month_matches[i+1].start() if i+1 < len(month_matches) else len(text)
    months[month] = text[start:end]

def split_slides(month_text):
    matches = list(slide_pattern.finditer(month_text))
    slides = {}
    for i, m in enumerate(matches):
        sn = int(m.group(1))
        s = m.end()
        e = matches[i+1].start() if i+1 < len(matches) else len(month_text)
        slides[sn] = month_text[s:e]
    return slides


def join_no_space(slide_text):
    """Concat all lines, strip [images:..] line, remove all whitespace."""
    lines = [ln for ln in slide_text.splitlines() if not ln.startswith("[images:")]
    joined = "".join(lines)
    return re.sub(r"\s+", "", joined)


def extract_progress(slide1_text):
    """Return list of (progress_actual, progress_plan_ratio, manpower_total, manpower_manager, manpower_partner).
    Order in slide is typically tank6 first, tank78 second.
    Two formats:
      A) 공정률 : XX.X% (계획比 YY.Y%), 일 평균 출력 : NNN명 (관리자: AA명, 협력사: BB명)
      B) 공정률 : 계획 PP.P% 실적 XX.X% (계획比 YY.Y%), 일 평균 출력 : NNN명 (관리자: AA명, 협력사: BB명)
    Returns (kind, actual, ratio, total, mgr, partner) tuples."""
    nows = join_no_space(slide1_text)
    # Format B - 계획 first, 실적 second (계획比 may be deviation, can be +/- signed, may have %p suffix)
    prog_re_b = re.compile(
        r"공정률:?계획(\d+(?:\.\d+)?)%?,?실적(\d+(?:\.\d+)?)%?\(?계획比([+-]?\d+(?:\.\d+)?)%p?\)?,?일?평균출력:?(\d+)명\(?관리자:?(\d+)명,?협력(?:사|업체):?(\d+)명\)?"
    )
    # Format A
    prog_re_a = re.compile(
        r"공정률:?(\d+(?:\.\d+)?)%?\(?계획比([+-]?\d+(?:\.\d+)?)%p?\)?,?일?평균출력:?(\d+)명\(?관리자:?\s?(\d+)명,?협력(?:사|업체):?\s?(\d+)명\)?"
    )
    # First find B matches and remember positions; then find A matches in remaining text.
    b_matches = list(prog_re_b.finditer(nows))
    matches = []  # tuples: (start_pos, actual, ratio, total, mgr, partner, plan_pct_or_None, context_hint)
    consumed_spans = []
    for bm in b_matches:
        plan_pct = float(bm.group(1))
        actual = float(bm.group(2))
        ratio = float(bm.group(3))
        total = int(bm.group(4))
        mgr = int(bm.group(5))
        partner = int(bm.group(6))
        ctx = classify_context(nows, bm.start())
        matches.append((bm.start(), actual, ratio, total, mgr, partner, plan_pct, ctx))
        consumed_spans.append((bm.start(), bm.end()))
    # Now find A matches not overlapping with B matches
    for am in prog_re_a.finditer(nows):
        s, e = am.start(), am.end()
        # Skip if overlap with any B span
        if any(not (e <= bs or s >= be) for bs, be in consumed_spans):
            continue
        actual = float(am.group(1))
        ratio = float(am.group(2))
        total = int(am.group(3))
        mgr = int(am.group(4))
        partner = int(am.group(5))
        ctx = classify_context(nows, s)
        matches.append((s, actual, ratio, total, mgr, partner, None, ctx))
    matches.sort(key=lambda x: x[0])
    return matches, nows


def classify_context(nows, pos):
    """Classify which sub-project a 공정률 entry belongs to by looking at preceding context (up to ~200 chars)."""
    look = nows[max(0, pos-400):pos]
    local = nows[max(0, pos-30):pos]
    # 종합공정률 - very local marker
    if "종합" in local:
        return "tank78_total"
    # Harbor sub-project markers
    harbor_keys = ["항만시설건설공사", "항만공사", "○항만"]
    last_harbor = max((look.rfind(k) for k in harbor_keys), default=-1)
    # Tank section markers
    t78_keys = ["2.#7,8탱크", "#7,8탱크증설공사", "■#7,8탱크", "○#7,8탱크"]
    t6_keys = ["1.#6탱크", "■#6탱크", "○#6탱크"]
    last78 = max((look.rfind(k) for k in t78_keys), default=-1)
    last6 = max((look.rfind(k) for k in t6_keys), default=-1)
    # Determine which anchor is closest before pos
    candidates = []
    if last_harbor >= 0:
        candidates.append((last_harbor, "tank6_harbor"))
    if last78 >= 0:
        candidates.append((last78, "tank78"))
    if last6 >= 0:
        candidates.append((last6, "tank6"))
    if candidates:
        # pick the most recent
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None


def get_lines(slide_text):
    """Get list of stripped non-empty lines (excluding image marker)."""
    lines = []
    for ln in slide_text.splitlines():
        if ln.startswith("[images:"):
            continue
        s = ln.strip()
        if s:
            lines.append(s)
    return lines


def extract_safety_audit(slide2_text):
    """Find 소계 row in 안전관리 실적 table.
    Categories order: 추락 / 전도 / 낙하·비래 / 감전 / 충돌·협착 / 붕괴·도괴 / 화재·폭발 / 질식 / 기타
    Then 금월합계 / 누계 -> 11 numbers total.
    Returns dict of category -> int, plus 'monthly_total' and 'cumulative'."""
    lines = get_lines(slide2_text)
    cats = ["추락", "전도", "낙하·비래", "감전", "충돌·협착", "붕괴·도괴", "화재·폭발", "질식", "기타"]
    # Find idx of "소계"
    try:
        idx = lines.index("소계")
    except ValueError:
        return None
    # Collect numeric or '-' tokens following 소계 - up to 11
    nums = []
    i = idx + 1
    while i < len(lines) and len(nums) < 11:
        ln = lines[i]
        # Strip commas (used as thousand separators) for parsing
        ln_stripped = ln.replace(",", "")
        if re.fullmatch(r"\d+", ln_stripped):
            nums.append(int(ln_stripped))
        elif ln == "-":
            nums.append(None)
        else:
            break
        i += 1
    if len(nums) < 9:
        return None
    result = {c: nums[k] if k < len(nums) else None for k, c in enumerate(cats)}
    result["금월합계"] = nums[9] if len(nums) >= 10 else None
    result["누계"] = nums[10] if len(nums) >= 11 else None
    return result


def extract_section_lines(slide1_text):
    """Split slide 1 into tank6 section and tank78 section based on '#6 탱크 증설공사' / '#7,8 탱크 증설공사'.
    Return dict: tank6_text, tank78_text."""
    # Use line-joined-with-newline approach but work on flat
    flat = "\n".join(get_lines(slide1_text))
    # Find positions
    nows = re.sub(r"\s+", "", flat)
    return flat, nows


def extract_tank78_section(slide1_text):
    """Extract the tank78 section bullets (between 2.#7,8/■#7,8/○#7,8 anchor and next/end).
    Return the lines that compose the tank78 section."""
    lines = get_lines(slide1_text)
    # Find tank78 anchor
    start = None
    for i, ln in enumerate(lines):
        # Look for header line containing #7,8 or 7,8 탱크
        if ("#7,8" in ln) or ("#7" in ln and "8" in ln and "탱크" in ln):
            start = i
            break
    if start is None:
        return []
    # End: next major section or end of slide
    end = len(lines)
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        # Markers that indicate tank78 section ended
        if "종합공정률" in ln or "■ 항만시설" in ln or "■항만시설" in ln or "■ 안전관리 실적" in ln:
            end = j
            break
    return lines[start:end]


def extract_photos(slide_text):
    """Extract photo captions from a slide that contains '공정 사진' or '안전점검 사진'."""
    flat = "\n".join(get_lines(slide_text))
    # Heuristic: collect all lines. We won't do heavy parsing.
    return get_lines(slide_text)


# ============ Main extraction ============
result = {}
missing = {}

for month, mtext in months.items():
    slides = split_slides(mtext)
    entry = {
        "tank6": None,
        "tank78": None,
        "tank6_harbor": None,
        "tank78_total": None,
        "tank78_section_lines": [],
        "safety_audit": None,
        "safety_audit_slide": None,
        "photos_slides": [],
    }
    miss = []

    # slide 1 -> progress
    if 1 in slides:
        matches, nows = extract_progress(slides[1])
        # Each match: (pos, actual, ratio, total, mgr, partner, plan_pct_or_None, ctx)
        def to_obj(m):
            return {
                "progress_actual": m[1],
                "progress_plan_ratio": m[2],
                "progress_plan_pct": m[6],
                "manpower_total": m[3],
                "manpower_manager": m[4],
                "manpower_partner": m[5],
            }
        # Detect whether #6 탱크 is reported in this slide.
        # Use both the joined-no-space and a more relaxed search
        has_tank6 = ("#6탱크" in nows or "1.#6" in nows or "■#6" in nows or "○#6" in nows)
        # Group by context
        assigned = {"tank6": None, "tank78": None, "tank6_harbor": None, "tank78_total": None}
        unassigned = []
        ordered = sorted(matches, key=lambda x: x[0])
        for m in ordered:
            ctx = m[7]
            if ctx in assigned and assigned[ctx] is None:
                assigned[ctx] = m
            else:
                unassigned.append(m)
        # Resolve unassigned matches.
        # Convention:
        #   - If #6 탱크 is reported in this slide, the FIRST unassigned (top of slide, no preceding header) is tank6.
        #   - If #6 탱크 is NOT reported, the first unassigned is tank78.
        for m in unassigned:
            if has_tank6 and assigned["tank6"] is None and m[0] < 250:
                assigned["tank6"] = m
            elif assigned["tank78"] is None:
                assigned["tank78"] = m
            elif assigned["tank6"] is None and has_tank6:
                assigned["tank6"] = m
            elif assigned["tank78_total"] is None:
                assigned["tank78_total"] = m
            elif assigned["tank6_harbor"] is None:
                assigned["tank6_harbor"] = m

        if assigned["tank6"]:
            entry["tank6"] = to_obj(assigned["tank6"])
        else:
            miss.append("tank6_progress")
        if assigned["tank78"]:
            entry["tank78"] = to_obj(assigned["tank78"])
        else:
            miss.append("tank78_progress")
        if assigned["tank6_harbor"]:
            entry["tank6_harbor"] = to_obj(assigned["tank6_harbor"])
        if assigned["tank78_total"]:
            entry["tank78_total"] = to_obj(assigned["tank78_total"])
        # Tank78 section text
        entry["tank78_section_lines"] = extract_tank78_section(slides[1])
    else:
        miss.append("slide1")

    # safety audit: search slides 2, 3 (2023-08 has labor strike on slide 2)
    audit = None
    audit_slide = None
    for sn in sorted(slides.keys()):
        if sn > 4:
            break
        cand = extract_safety_audit(slides[sn])
        if cand:
            audit = cand
            audit_slide = sn
            break
    entry["safety_audit"] = audit
    entry["safety_audit_slide"] = audit_slide
    if not audit:
        miss.append("safety_audit (no 소계 row)")

    # remaining slides -> photo metadata (collect captions)
    boiler = {"광양", "LNG", "터미널 증설공사", "터미널증설공사", "월 간 업 무 보 고", "월간 업무 보고",
              "월 간", "월", "○", "■", "광양 ", ".", ","}
    for sn in sorted(slides.keys()):
        # Skip slide 1 (progress) and the slide that had the safety audit
        if sn == 1:
            continue
        if sn == entry.get("safety_audit_slide"):
            continue
        sl_lines = get_lines(slides[sn])
        joined_first = "\n".join(sl_lines[:30])
        if "공정 사진" in joined_first or "공정사진" in joined_first:
            kind = "공정사진"
        elif "안전점검" in joined_first:
            kind = "안전점검"
        elif "항만" in joined_first or "해상부" in joined_first:
            kind = "항만/해상"
        else:
            kind = "기타"
        # Captions: filter to lines that look like meaningful titles (have date or descriptive text)
        captions = []
        for ln in sl_lines:
            # Skip pure ’23./’24./month labels
            if re.fullmatch(r"['‘’]\d{2}\.[\s\d./~]*", ln):
                continue
            if re.fullmatch(r"\d+", ln):
                continue
            captions.append(ln)
        entry["photos_slides"].append({
            "slide": sn,
            "kind": kind,
            "captions": captions[:60],
        })

    result[month] = entry
    if miss:
        missing[month] = miss

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Save JSON
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"data": result, "missing": missing}, f, ensure_ascii=False, indent=2)

# Summary
print(f"Total months processed: {len(result)}")
for m, e in result.items():
    t6 = e["tank6"]["progress_actual"] if e["tank6"] else None
    t78 = e["tank78"]["progress_actual"] if e["tank78"] else None
    audit_ok = "OK" if e["safety_audit"] else "MISSING"
    photos = len(e["photos_slides"])
    print(f"  {m}: tank6={t6}, tank78={t78}, safety={audit_ok}, photos_slides={photos}")

print("\nMissing items per month:")
for m, items in missing.items():
    print(f"  {m}: {items}")
