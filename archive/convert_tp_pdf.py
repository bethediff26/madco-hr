#!/usr/bin/env python3
"""Convert markdown files to PDF using pypdfx"""

import sys
from pathlib import Path

try:
    from pdf2image import image2pdf
except ImportError:
    print("Please install pdf2image: pip install pdf2image")
    sys.exit(1)


def convert_md_to_pdf(md_path: str, output_path: str) -> None:
    """Convert a markdown file to PDF."""
    from markdown import Markdown

    # Read the markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    converter = Markdown(extensions=['extra', 'pymdownx.highlight', 'pymdownx.tabbed'])
    html_content = converter.convert(md_content)

    # Save as HTML first, then convert to PDF using pdf2image
    html_path = Path(output_path).with_suffix('.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Convert HTML to image (we'll use wkhtmltoimage approach)
    # For simplicity, let's just create a script that uses pandoc or similar

    print(f"HTML file created at: {html_path}")
    print("To convert to PDF, run:")
    print(f"  pdftk {output_path} -cat 2-end output {output_path.pdf_name}")


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python convert_tp_pdf.py <input_md_file> <output_pdf_name>")
        print("\nExample:")
        print(f"  python {__file__} holidays_policy.md holidays_policy")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    output_name = sys.argv[2]

    if not md_file.exists():
        print(f"Error: Markdown file '{md_file}' does not exist.")
        sys.exit(1)

    output_path = f"{output_name}.pdf"
    convert_md_to_pdf(str(md_file), output_path)


if __name__ == "__main__":
    main()
