#!/usr/bin/env python3
"""Convert markdown files to PDF using tkinter's tktext widget."""

import sys
import tkinter as tk
from tkinter import Text, Tk
from pathlib import Path


def convert_md_to_pdf(md_path: str, output_path: str = None) -> None:
    """Convert a markdown file to PDF using tkinter's save_as method."""

    md_file = Path(md_path).resolve()

    if not md_file.exists():
        print(f"Error: Markdown file '{md_file}' does not exist.")
        sys.exit(1)

    if output_path is None:
        output_path = str(md_file.with_suffix('.pdf').resolve())
    else:
        output_path = Path(output_path).resolve()

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create root window (hidden)
    root = Tk()
    root.withdraw()
    root.overrideredirect(True)

    # Create text widget
    text_widget = Text(root, wrap='word', font=('Helvetica', 10))
    text_widget.pack(fill='both', expand=True)

    # Insert content with formatting
    lines = content.split('\n')
    for line in lines:
        if line.startswith('### '):
            text_widget.insert(tk.END, '\n' + line[3:] + '\n\n')
            text_widget.tag_configure('heading-3', font=('Helvetica', 12, 'bold'))
            text_widget.tag_add('heading-3', 'end-4c', 'end-1c')
        elif line.startswith('## '):
            text_widget.insert(tk.END, '\n' + line[2:] + '\n\n')
            text_widget.tag_configure('heading-2', font=('Helvetica', 14, 'bold'))
            text_widget.tag_add('heading-2', 'end-5c', 'end-1c')
        elif line.startswith('# '):
            text_widget.insert(tk.END, '\n' + line[2:] + '\n\n\n')
            text_widget.tag_configure('heading-1', font=('Helvetica', 18, 'bold'))
            text_widget.tag_add('heading-1', 'end-6c', 'end-1c')
        elif '`' in line:
            # Code snippet
            text_widget.insert(tk.END, '\n' + line + '\n')
            text_widget.tag_configure('code', font=('Courier New', 10), foreground='#333333')
            text_widget.tag_add('code', 'end-2c', 'end-1c')
        elif '*' in line and '**' not in line:
            # Italic or bold
            line = line.replace('*', '').replace('_', '')
            text_widget.insert(tk.END, line + '\n')
        else:
            text_widget.insert(tk.END, line + '\n')

    # Tag the rest as normal text
    text_widget.tag_configure('normal', font=('Helvetica', 10), justify='left')
    text_widget.tag_add('normal', '1.0', 'end-1c')

    # Set background and foreground colors
    text_widget.config(bg='white', fg='black')

    # Scrollbar
    scrollbar = tk.Scrollbar(text_widget)
    scrollbar.pack(side=RIGHT, fill=Y)
    text_widget.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=text_widget.yview)

    # Save as PDF
    try:
        text_widget.save_as(master=root, filename=str(output_path))
        print(f"PDF created at: {output_path}")
    except Exception as e:
        print(f"Error saving PDF: {e}")
        root.destroy()
        sys.exit(1)

    # Cleanup
    root.destroy()


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python convert_to_pdf.py <markdown_file> [output_filename]")
        print("\nExamples:")
        print(f"  python {sys.argv[0]} holidays_policy.md")
        print(f"  python {sys.argv[0]} document.md output.pdf")
        sys.exit(1)

    md_file = Path(sys.argv[1])

    if not md_file.exists():
        print(f"Error: Markdown file '{md_file}' does not exist.")
        sys.exit(1)

    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    convert_md_to_pdf(str(md_file), output_name)


if __name__ == "__main__":
    main()
