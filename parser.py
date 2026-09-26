"""Document parsing and chunking utilities for RAG pipeline."""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Union

# Try to import pypdf with fallback
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

MAX_TOKENS_PER_CHUNK = 400
OVERLAP_TOKENS = 50


def parse_markdown(file_path: str) -> Dict[str, Any]:
    """Read and parse a Markdown policy file.

    Args:
        file_path: Path to the .md file

    Returns:
        Dictionary containing 'doc_id', 'doc_title', and 'content'
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract document ID from filename
    file_name = os.path.basename(file_path)
    doc_id = file_name.replace(".md", "").lstrip("-_").lower().replace("-", "_")

    # Check for YAML frontmatter (--- ... ---) - but only at the very start
    if content.strip().startswith("---"):
        lines = content.split("\n")
        frontmatter_lines = []
        document_lines = []

        in_frontmatter = False
        for line in lines:
            stripped = line.strip()

            # First --- starts frontmatter (only if we're not already in it)
            if not in_frontmatter and stripped == "---":
                in_frontmatter = True
            # Second --- ends frontmatter - transition to document mode, don't add this line
            elif in_frontmatter and stripped == "---":
                in_frontmatter = False
                # Skip the closing --- line entirely - don't add to any list
            elif in_frontmatter:
                frontmatter_lines.append(line)
            else:
                document_lines.append(line)

        frontmatter_text = "\n".join(frontmatter_lines)
        document_content = "\n".join(document_lines)

        # Parse frontmatter for metadata
        title_match = re.search(r'^title:\s*(.+)$', frontmatter_text, re.IGNORECASE)
        if title_match:
            doc_title = title_match.group(1).strip()
        else:
            doc_title = file_name.replace(".md", "")

    else:
        document_content = content
        doc_title = file_name.replace(".md", "").lstrip("-_").lower().replace("-", "_")

    return {
        "doc_id": doc_id,
        "doc_title": doc_title,
        "content": document_content
    }


def parse_pdf(file_path: str) -> Dict[str, Any]:
    """Extract text from a PDF file using pypdf.

    Args:
        file_path: Path to the .pdf file

    Returns:
        Dictionary containing 'doc_id', 'doc_title', and 'content'
    """
    if not PYPDF_AVAILABLE:
        raise ImportError("pypdf is required for PDF parsing. Install with: pip install pypdf")

    reader = PdfReader(file_path)
    page_count = len(reader.pages)

    # Extract text from all pages and join with spaces
    full_text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        full_text += page_text + "\n\n"

    # Use filename as doc_id and title (can be updated if PDF metadata exists)
    file_name = os.path.basename(file_path)
    doc_id = file_name.replace(".pdf", "")
    doc_title = f"{file_name} (PDF)"

    return {
        "doc_id": doc_id,
        "doc_title": doc_title,
        "content": full_text.strip()
    }


def tokenize(text: str) -> List[str]:
    """Simple tokenizer: split on whitespace and punctuation.

    Args:
        text: Input text to tokenize

    Returns:
        List of tokens
    """
    # Tokenize while keeping some common delimiters for context
    tokens = re.findall(r'\b[\w\-.]+(?:[^\w\d"\'\-]*[^\w\d"\'\-])*[\w]\b', text)
    return [t.strip() for t in tokens if t.strip()]


def count_tokens(text: str) -> int:
    """Count tokens using a simple heuristic (10 chars ≈ 1 token).

    Args:
        text: Input text

    Returns:
        Approximate token count
    """
    # More accurate than character count but simpler than real tokenizer
    words = text.split()
    return max(1, sum(len(w) for w in words))


def _slide_window_chunking(text: str, max_tokens: int, overlap_tokens: int) -> List[str]:
    """Token sliding window chunking.

    Args:
        text: Input text
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Number of overlapping tokens between chunks

    Returns:
        List of chunk texts
    """
    tokens = tokenize(text)
    token_list = list(enumerate(tokens))
    total_tokens = len(token_list)

    if total_tokens <= max_tokens:
        return [text]  # Return entire text as single chunk

    chunks = []
    window_size = max_tokens - overlap_tokens

    for i in range(0, total_tokens, window_size):
        start_idx = i
        end_idx = min(i + window_size, total_tokens)

        # Expand backward to include more tokens if we're hitting the limit
        while start_idx > 0 and count_tokens("".join(token_list[start_idx:end_idx])) > max_tokens:
            start_idx -= 1

        chunk_tokens = [token for idx, token in token_list[start_idx:end_idx]]
        chunks.append(" ".join(chunk_tokens))

        # Expand forward if we have extra tokens at the end of window
        while end_idx < total_tokens and count_tokens("".join(chunk_tokens + [token for idx, token in token_list[end_idx:min(end_idx + 3, total_tokens)]])) <= max_tokens:
            end_idx += 1

    return chunks


def _heading_aware_chunking(content: str) -> List[tuple]:
    """Split document by Markdown headers, respecting section boundaries.

    Args:
        content: Document content with Markdown headers

    Returns:
        List of (section_title, text) tuples
    """
    # Regex to match Markdown headers (#, ##, ###, etc.)
    header_pattern = r'^(#+)\s+(.+)$'

    lines = content.split("\n")
    sections = []
    current_section_title = None
    current_section_text = []

    for line in lines:
        match = re.match(header_pattern, line)

        if match:
            # Save previous section if exists
            if current_section_title is not None:
                sections.append((current_section_title, "\n".join(current_section_text)))

            # Start new section
            current_section_title = f"{match.group(1)} {match.group(2).strip()}"
            current_section_text = [line]
        else:
            # Add non-header line to current section
            current_section_text.append(line)

    # Don't forget the last section
    if current_section_title is not None:
        sections.append((current_section_title, "\n".join(current_section_text)))

    return sections


def chunk_document(content: str, doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
    """Split document into chunks using heading-aware strategy.

    If a section exceeds 400 words (tokens), fall back to token sliding windows
    with overlapping margins within the section.

    Args:
        content: Full document text
        doc_id: Document ID for metadata
        doc_title: Document title for metadata

    Returns:
        List of chunk dictionaries with keys:
        - chunk_id: Unique chunk identifier
        - doc_id: Document ID
        - doc_title: Document title
        - section: Section title (or 'document' if no sections found)
        - text: Chunk text
    """
    chunks = []

    # First, split by Markdown headers to identify sections
    sections = _heading_aware_chunking(content)

    chunk_counter = 0

    for section_idx, (section_title, section_text) in enumerate(sections):
        # Count tokens in this section
        section_tokens = count_tokens(section_text)

        if section_tokens <= MAX_TOKENS_PER_CHUNK:
            # Section is small enough, add as single chunk
            chunks.append({
                "chunk_id": f"{doc_id}-{section_idx:03d}",
                "doc_id": doc_id,
                "doc_title": doc_title,
                "section": section_title,
                "text": section_text
            })
        else:
            # Section is large, use sliding window within this section
            sub_chunks = _slide_window_chunking(section_text, MAX_TOKENS_PER_CHUNK, OVERLAP_TOKENS)

            for idx, chunk_text in enumerate(sub_chunks):
                chunks.append({
                    "chunk_id": f"{doc_id}-{section_idx:03d}-{idx:02d}",
                    "doc_id": doc_id,
                    "doc_title": doc_title,
                    "section": section_title,
                    "text": chunk_text
                })

    return chunks


def load_and_parse_policies(policies_dir: str = "data/policies") -> List[Dict[str, Any]]:
    """Scan directory for .md and .pdf files, parse them, and return structured chunks.

    Args:
        policies_dir: Path to directory containing policy files

    Returns:
        Complete list of chunk dictionaries from all parsed documents
    """
    # Validate directory exists
    if not os.path.isdir(policies_dir):
        raise ValueError(f"Policy directory does not exist: {policies_dir}")

    all_chunks = []

    # Get list of supported files in directory
    policy_extensions = [".md", ".pdf"]

    # Process markdown files
    md_files = []
    pdf_files = []

    for file_path in os.listdir(policies_dir):
        if any(file_path.endswith(ext) for ext in policy_extensions):
            if file_path.endswith(".md"):
                md_files.append(os.path.join(policies_dir, file_path))
            elif file_path.endswith(".pdf"):
                pdf_files.append(os.path.join(policies_dir, file_path))

    # Parse markdown files
    for file_path in sorted(md_files):
        try:
            parsed = parse_markdown(file_path)
            chunks = chunk_document(
                content=parsed["content"],
                doc_id=parsed["doc_id"],
                doc_title=parsed["doc_title"]
            )
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")

    # Parse PDF files
    for file_path in sorted(pdf_files):
        try:
            parsed = parse_pdf(file_path)
            chunks = chunk_document(
                content=parsed["content"],
                doc_id=parsed["doc_id"],
                doc_title=parsed["doc_title"]
            )
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")

    # Sort chunks by chunk_id for consistent ordering
    all_chunks.sort(key=lambda x: x["chunk_id"])

    return all_chunks
