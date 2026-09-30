"""Test script for parser module."""

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())
import parser


def test_parse_markdown():
    """Test markdown parsing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        content = """---
title: Company Policy
---

# Introduction

This is a sample company policy.

## Section One

More text in this section.

### Subsection

Even more detail here.

---

# Appendix A

Additional information."""
        f.write(content)
        file_path = f.name

    try:
        result = parser.parse_markdown(file_path)
        assert result["doc_id"] == "company-policy", f"Expected 'company-policy', got '{result['doc_id']}'"
        assert result["doc_title"] == "Company Policy", f"Expected 'Company Policy', got '{result['doc_title']}'"
        assert "Introduction" in result["content"], f"Content should contain 'Introduction', got: {result['content']}"
        print("✓ parse_markdown works correctly")
        return True
    finally:
        os.unlink(file_path)


def test_parse_pdf():
    """Test PDF parsing (requires pypdf)."""
    if not parser.PYPDF_AVAILABLE:
        # Create a minimal valid PDF for testing
        import struct
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as f:
            # Minimal PDF structure
            f.write(b"%PDF-1.4\n")
            f.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
            f.write("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
            f.write("3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R /MediaBox [0 0 612 792] >>\nendobj\n")
            f.write("4 0 obj\n<< /Length 15 >>\nstream\nBT\n/F1 12 Tf\n48 720 Td\n(Test PDF Document)\n(Tj)\nET\nendstream\nendobj\n")
            f.write("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
            f.write("xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000053 00000 n \n0000000106 00000 n \n0000000176 00000 n \n0000000249 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n358\n%%%%EOF\n")
            pdf_path = f.name

        try:
            result = parser.parse_pdf(pdf_path)
            assert result["doc_id"] == "tmp", f"Expected 'tmp', got '{result['doc_id']}'"
            assert "Test PDF Document" in result["content"], f"Content should contain 'Test PDF Document', got: {result['content']}"
            print("✓ parse_pdf works correctly")
            return True
        finally:
            os.unlink(pdf_path)
    else:
        # Use an existing PDF file if available for testing
        pdf_files = list(Path(".pdf").glob("*.pdf"))
        if not pdf_files:
            print("⚠ Skipping parse_pdf test (no PDF files found and pypdf may not be installed)")
            return True


def test_chunk_document():
    """Test document chunking."""
    content = """# Introduction

This is the introduction section of our company policy. It sets the stage for understanding all policies that employees need to be aware of. We are committed to creating a safe and productive work environment.

## Code of Conduct

All employees must adhere to the following code of conduct at all times during their employment with our organization.

### Professional Behavior

Maintain professional communication in all channels including email, Slack, and in-person interactions. Respect colleagues from diverse backgrounds.

## Security Policy

Our security policy outlines key requirements for handling company data. All employees must secure their credentials and report any suspicious activity immediately.

### Data Protection

Protect sensitive information by using strong passwords and multi-factor authentication."""

    chunks = parser.chunk_document(content, doc_id="test-doc", doc_title="Test Document")

    assert len(chunks) > 0, "Should create at least one chunk"
    assert all("chunk_id" in c for c in chunks), "All chunks should have 'chunk_id'"
    assert all("doc_id" in c for c in chunks), "All chunks should have 'doc_id'"
    assert all("doc_title" in c for c in chunks), "All chunks should have 'doc_title'"
    assert all("section" in c for c in chunks), "All chunks should have 'section'"
    assert all("text" in c for c in chunks), "All chunks should have 'text'"

    # Check that section names are extracted correctly (without hash prefix)
    sections_found = set(c["section"] for c in chunks)
    assert "Introduction" in sections_found, f"'Introduction' not found in sections: {sections_found}"
    assert "Code of Conduct" in sections_found, f"'Code of Conduct' not found in sections: {sections_found}"
    assert "Security Policy" in sections_found, f"'Security Policy' not found in sections: {sections_found}"

    print(f"✓ chunk_document works correctly (created {len(chunks)} chunks)")
    return True


def test_load_and_parse_policies():
    """Test loading and parsing multiple files."""
    # Create a temporary directory with sample files
    with tempfile.TemporaryDirectory() as tmpdir:
        policies_dir = os.path.join(tmpdir, "policies")
        os.makedirs(policies_dir)

        # Create a sample markdown file
        md_content = """# Access Control

Employees must use approved devices for accessing company systems.

## Device Requirements

All company laptops must have the latest security patches installed."""

        with open(os.path.join(policies_dir, "Access_Control.md"), "w") as f:
            f.write(md_content)

        # Parse policies directory
        chunks = parser.load_and_parse_policies(policies_dir)

        assert len(chunks) > 0, "Should create at least one chunk"
        chunk_ids = [c["chunk_id"] for c in chunks]

        # Section title should match without hash prefix and with proper casing
        section_title = "Access Control"
        assert all(c["section"] == section_title for c in chunks), \
            f"All chunks should have section '{section_title}', got: {[c['section'] for c in chunks]}"

        print(f"✓ load_and_parse_policies works correctly ({len(chunks)} chunks loaded)")
        return True


if __name__ == "__main__":
    import sys

    tests = [
        ("parse_markdown", test_parse_markdown),
        ("chunk_document", test_chunk_document),
        ("load_and_parse_policies", test_load_and_parse_policies),
        ("parse_pdf", test_parse_pdf),
    ]

    print("Running parser tests...\n")

    failed = []
    for name, func in tests:
        try:
            if not func():
                failed.append(name)
        except Exception as e:
            print(f"✗ {name} FAILED with exception: {e}")
            failed.append(name)

    print("\n" + "="*50)
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed")
        for name in failed:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED ✓")
