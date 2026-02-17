from __future__ import annotations
import os
from dataclasses import dataclass
from reportlab.lib import colors

@dataclass
class PdfTheme:
    name: str = "artbiz_default"
    font_family: str = "Helvetica"     # will be overridden if Korean font is registered
    font_family_bold: str = "Helvetica-Bold"
    primary: any = colors.HexColor("#222222")
    secondary: any = colors.HexColor("#666666")
    accent: any = colors.HexColor("#0B57D0")
    table_header_bg: any = colors.HexColor("#F3F4F6")
    table_grid: any = colors.HexColor("#D1D5DB")

def get_theme() -> PdfTheme:
    # future: choose by env THEME
    return PdfTheme()
