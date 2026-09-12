"""
layout_parser.py - Spatial Layout-Aware Multi-Column PDF Parser
Uses Bounding-Box coordinate clustering to preserve reading order in 1-column and 2-column resumes.
"""
import fitz  # PyMuPDF
from typing import List, Dict, Any


def parse_pdf_layout_aware(pdf_path: str) -> Dict[str, Any]:
    """
    Parses a PDF document while preserving spatial reading order.
    Detects two-column layouts vs single-column layouts and orders blocks appropriately.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {
            "text": "",
            "diagnostics": [],
            "error": str(e)
        }

    full_ordered_pages: List[str] = []
    page_diagnostics: List[Dict[str, Any]] = []

    for page_idx, page in enumerate(doc):
        # Extract blocks: (x0, y0, x1, y1, text, block_no, block_type)
        blocks = page.get_text("blocks")
        page_width = page.rect.width
        page_height = page.rect.height

        # Filter for text blocks with non-empty text (block_type 0 is text)
        text_blocks = [
            b for b in blocks 
            if len(b) >= 7 and b[6] == 0 and b[4] and b[4].strip()
        ]

        if not text_blocks:
            continue

        midpoint = page_width / 2.0
        
        # Segment blocks into Left, Right, and Spanning (full-width header/footer)
        left_blocks: List[Any] = []
        right_blocks: List[Any] = []
        spanning_blocks: List[Any] = []

        for b in text_blocks:
            x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
            # If block starts well into left and extends well into right, it spans both columns
            is_spanning = (x0 < (midpoint - 40)) and (x1 > (midpoint + 40))

            if is_spanning:
                spanning_blocks.append(b)
            elif x1 <= (midpoint + 25):
                left_blocks.append(b)
            elif x0 >= (midpoint - 25):
                right_blocks.append(b)
            else:
                # Majority overlap
                center_x = (x0 + x1) / 2.0
                if center_x < midpoint:
                    left_blocks.append(b)
                else:
                    right_blocks.append(b)

        # Decide if page has a genuine 2-column structure
        if left_blocks and right_blocks:
            left_avg_x0 = sum(b[0] for b in left_blocks) / len(left_blocks)
            right_avg_x0 = sum(b[0] for b in right_blocks) / len(right_blocks)
            # Clear horizontal column separation
            has_separation = (right_avg_x0 - left_avg_x0) > (page_width * 0.20)
            is_two_column = has_separation and ((len(left_blocks) + len(right_blocks)) >= 2)
        else:
            is_two_column = False

        ordered_blocks: List[Any] = []
        if is_two_column:
            # Separate top header blocks: spanning blocks or left blocks that sit strictly above the right column
            min_right_y0 = min(b[1] for b in right_blocks) if right_blocks else page_height
            top_left_headers = [b for b in left_blocks if b[3] <= min_right_y0 + 5]
            col_left_blocks = [b for b in left_blocks if b[3] > min_right_y0 + 5]

            top_headers = [b for b in spanning_blocks if b[1] < (page_height * 0.35)] + top_left_headers
            bottom_footers = [b for b in spanning_blocks if b[1] >= (page_height * 0.35)]

            # Sort top headers by vertical position
            top_headers.sort(key=lambda b: (b[1], b[0]))
            
            # Sort left column top-to-bottom
            col_left_blocks.sort(key=lambda b: (b[1], b[0]))
            
            # Sort right column top-to-bottom
            right_blocks.sort(key=lambda b: (b[1], b[0]))
            
            # Sort bottom footers top-to-bottom
            bottom_footers.sort(key=lambda b: (b[1], b[0]))

            # Assembled natural reading order: Top Headers -> Left Column -> Right Column -> Bottom Footers
            ordered_blocks = top_headers + col_left_blocks + right_blocks + bottom_footers
        else:
            # Single-column: sort primarily by top-to-bottom (y0), secondary left-to-right (x0)
            text_blocks.sort(key=lambda b: (b[1], b[0]))
            ordered_blocks = text_blocks

        page_text = "\n\n".join(b[4].strip() for b in ordered_blocks if b[4].strip())
        full_ordered_pages.append(page_text)

        page_diagnostics.append({
            "page_number": page_idx + 1,
            "detected_layout": "2-column" if is_two_column else "single-column",
            "left_blocks_count": len(left_blocks),
            "right_blocks_count": len(right_blocks),
            "spanning_blocks_count": len(spanning_blocks),
            "total_blocks": len(ordered_blocks)
        })

    combined_text = "\n\n".join(full_ordered_pages)

    return {
        "text": combined_text,
        "total_pages": len(doc),
        "diagnostics": page_diagnostics
    }
