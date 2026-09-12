"""
anti_cheat.py - Adversarial Defense & Anti-Cheat Engine
Detects white-font keyword stuffing, invisible text (render mode/camouflaged RGB),
micro-fonts, and prompt injection attacks in resumes.
"""
import re
import fitz  # PyMuPDF
from typing import Dict, Any, List

PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)system\s+override",
    r"(?i)system\s*:\s*candidate\s+is\s+a\s+perfect\s+fit",
    r"(?i)give\s+(a\s+)?(perfect\s+score|100%|100/100)",
    r"(?i)rate\s+(this\s+candidate\s+)?(10\s*[/out of]\s*10|100\s*[/out of]\s*100)",
    r"(?i)you\s+must\s+(recommend|rate)\s+(interview|hire|accept)",
    r"(?i)hidden\s+instruction",
    r"(?i)forget\s+all\s+prior\s+rules",
    r"(?i)jailbreak",
    r"(?i)prompt\s+injection"
]


def scan_for_adversarial_tampering(pdf_path: str, extracted_text: str) -> Dict[str, Any]:
    """
    Scans a PDF for invisible text, microscopic fonts, off-canvas rendering,
    and prompt injection strings.
    """
    flags: List[Dict[str, Any]] = []
    suspicious_snippets: List[str] = []
    white_text_count = 0
    micro_font_count = 0
    out_of_bounds_count = 0

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {
            "is_compromised": False,
            "adversarial_flags_count": 0,
            "penalty_score": 0,
            "error": str(e)
        }

    for page_num, page in enumerate(doc):
        page_dict = page.get_text("dict")
        page_width = page.rect.width
        page_height = page.rect.height

        for block in page_dict.get("blocks", []):
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue

                    font_size = span.get("size", 10.0)
                    color_int = span.get("color", 0)

                    # Decompose RGB from 24-bit integer
                    r = (color_int >> 16) & 255
                    g = (color_int >> 8) & 255
                    b = color_int & 255

                    # 1. White / Camouflaged text on white background
                    is_white_font = (r >= 245 and g >= 245 and b >= 245)
                    
                    # 2. Microscopic font (< 2.5 pt)
                    is_micro_font = (font_size < 2.5)

                    # 3. Text placed outside visible boundaries
                    bbox = span.get("bbox", (0, 0, 0, 0))
                    is_out_of_bounds = (
                        bbox[0] < -10 or bbox[1] < -10 or 
                        bbox[2] > (page_width + 10) or bbox[3] > (page_height + 10)
                    )

                    if is_white_font or is_micro_font or is_out_of_bounds:
                        reasons = []
                        if is_white_font:
                            reasons.append(f"Camouflaged White Font (RGB: {r},{g},{b})")
                            white_text_count += 1
                        if is_micro_font:
                            reasons.append(f"Microscopic Font ({font_size:.1f}pt)")
                            micro_font_count += 1
                        if is_out_of_bounds:
                            reasons.append("Off-Canvas Boundary Placement")
                            out_of_bounds_count += 1

                        flags.append({
                            "page": page_num + 1,
                            "snippet": text[:80],
                            "reasons": reasons
                        })
                        suspicious_snippets.append(text)

    # 4. Check for Prompt Injections in text
    injections_detected = []
    for pattern in PROMPT_INJECTION_PATTERNS:
        matches = re.findall(pattern, extracted_text)
        if matches:
            injections_detected.append(pattern)

    is_compromised = len(flags) > 0 or len(injections_detected) > 0

    # Calculate penalty score
    penalty_score = 0
    if len(injections_detected) > 0:
        penalty_score += 60  # Severe prompt injection attempt
    if white_text_count > 0:
        penalty_score += min(40, white_text_count * 10)  # Keyword stuffing
    if micro_font_count > 0:
        penalty_score += min(30, micro_font_count * 10)
    if out_of_bounds_count > 0:
        penalty_score += min(30, out_of_bounds_count * 10)

    penalty_score = min(100, penalty_score)

    audit_status = "CLEAN"
    if len(injections_detected) > 0 and (white_text_count > 0 or micro_font_count > 0):
        audit_status = "CRITICAL_ATTACK_DETECTED"
    elif len(injections_detected) > 0:
        audit_status = "PROMPT_INJECTION_DETECTED"
    elif is_compromised:
        audit_status = "KEYWORD_STUFFING_FLAGGED"

    return {
        "is_compromised": is_compromised,
        "audit_status": audit_status,
        "penalty_score": penalty_score,
        "adversarial_flags_count": len(flags),
        "white_text_count": white_text_count,
        "micro_font_count": micro_font_count,
        "prompt_injections_found": len(injections_detected),
        "flagged_snippets": [f["snippet"] for f in flags[:5]],
        "detailed_flags": flags[:10]
    }
