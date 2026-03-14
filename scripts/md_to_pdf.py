"""Convert the CMS handleiding markdown to a styled PDF."""
from fpdf import FPDF
import re

FONT = "DejaVu"
MONO = "Mono"

class HandleidingPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font(FONT, "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "CMS Handleiding \u2014 sanderveen.art", align="R")
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT, "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")


def build_pdf(md_path, output_path):
    pdf = HandleidingPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    font_dir = "C:/Windows/Fonts/"
    pdf.add_font(FONT, "", font_dir + "arial.ttf", uni=True)
    pdf.add_font(FONT, "B", font_dir + "arialbd.ttf", uni=True)
    pdf.add_font(FONT, "I", font_dir + "ariali.ttf", uni=True)
    pdf.add_font(MONO, "", font_dir + "consola.ttf", uni=True)

    pdf.add_page()

    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    gold = (184, 134, 11)
    dark = (40, 40, 40)
    muted = (100, 100, 100)

    for line in lines:
        line = line.rstrip("\n")

        # H1
        if line.startswith("# ") and not line.startswith("##"):
            pdf.set_font(FONT, "B", 22)
            pdf.set_text_color(*dark)
            pdf.ln(5)
            pdf.cell(0, 12, line[2:])
            pdf.ln(10)
            pdf.set_draw_color(*gold)
            pdf.set_line_width(0.8)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(8)

        # H2
        elif line.startswith("## "):
            pdf.ln(6)
            pdf.set_font(FONT, "B", 14)
            pdf.set_text_color(*gold)
            pdf.cell(0, 10, line[3:])
            pdf.ln(8)

        # Numbered list
        elif re.match(r"^\d+\.\s", line):
            pdf.set_font(FONT, "", 11)
            pdf.set_text_color(*dark)
            write_rich_line(pdf, line.strip(), x_offset=12, dark=dark)
            pdf.ln(6)

        # Sub-item (indented with -)
        elif re.match(r"^\s+-\s", line):
            pdf.set_font(FONT, "", 10)
            pdf.set_text_color(*muted)
            text = line.strip().lstrip("- ")
            write_rich_line(pdf, f"  \u2022  {text}", x_offset=18, dark=dark, base_color=muted)
            pdf.ln(5)

        # Bullet list
        elif line.startswith("- "):
            pdf.set_font(FONT, "", 11)
            pdf.set_text_color(*dark)
            text = line[2:].strip()
            write_rich_line(pdf, f"\u2022  {text}", x_offset=12, dark=dark)
            pdf.ln(6)

        # Empty line
        elif line.strip() == "":
            pdf.ln(3)

        # Normal paragraph
        else:
            pdf.set_font(FONT, "", 11)
            pdf.set_text_color(*dark)
            write_rich_line(pdf, line.strip(), x_offset=10, dark=dark)
            pdf.ln(6)

    pdf.output(output_path)
    print(f"PDF saved to: {output_path}")


def write_rich_line(pdf, text, x_offset=10, dark=(40, 40, 40), base_color=None):
    """Write a line with **bold** and `code` formatting."""
    if base_color is None:
        base_color = dark
    pdf.set_x(x_offset)
    parts = re.split(r'(\*\*.*?\*\*|`[^`]+`)', text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font(FONT, "B", pdf.font_size_pt)
            pdf.set_text_color(*dark)
            pdf.write(6, part[2:-2])
            pdf.set_font(FONT, "", pdf.font_size_pt)
            pdf.set_text_color(*base_color)
        elif part.startswith("`") and part.endswith("`"):
            pdf.set_font(MONO, "", pdf.font_size_pt - 1)
            pdf.set_text_color(100, 100, 100)
            pdf.write(6, part[1:-1])
            pdf.set_font(FONT, "", pdf.font_size_pt)
            pdf.set_text_color(*base_color)
        else:
            pdf.write(6, part)


if __name__ == "__main__":
    build_pdf(
        r"C:\local_dev\sanderveen.nl\docs\CMS-HANDLEIDING.md",
        r"C:\Users\scbry\Downloads\CMS-Handleiding-SanderVeen.pdf",
    )
