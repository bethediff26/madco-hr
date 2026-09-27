"""Policy document parser with heading-aware chunking."""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a policy document chunk with rich metadata."""
    chunk_id: int
    doc_id: str
    doc_title: str
    section: str
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "doc_title": self.doc_title,
            "section": self.section,
            "text": self.text
        }


class PolicyParser:
    """Parser for policy documents (.md and .pdf)."""

    def __init__(self, policies_dir: str = "data/policies"):
        """Initialize parser with path to policy directory."""
        self.policies_dir = os.path.abspath(policies_dir)
        self.chunk_counter = 0

    def read_document(self, file_path: str) -> str:
        """Read document content based on file extension.

        Args:
            file_path: Path to the document file

        Returns:
            Raw text content of the document
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            try:
                import pypdf
                with open(file_path, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    # Extract text from all pages
                    full_text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        full_text += page.extract_text() or ""
                return full_text
            except ImportError:
                logger.warning(f"pypdf not installed, unable to parse PDF file: {file_path}")
                return ""
        elif ext == ".md":

            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def parse_markdown_headers(self, text: str) -> List[tuple]:
        """Parse Markdown headers from text.

        Args:
            text: Document text

        Returns:
            List of tuples (level, heading_text) for each header found
        """
        headers = []
        # Match MDX-style headers (# and ##)
        pattern = r'^(#{1,2})\s+(.+)$'

        lines = text.split('\n')
        for line in lines:
            match = re.match(pattern, line.strip())
            if match:
                level = len(match.group(1))
                heading_text = match.group(2).strip()
                headers.append((level, heading_text))

        return headers

    def extract_sections(self, text: str) -> List[tuple]:
        """Extract sections from document based on headers.

        Args:
            text: Document text

        Returns:
            List of (section_title, section_text) tuples
        """
        pattern = r'^(#{1,2})\s+(.+)$'

        # Split by headers
        parts = re.split(pattern, text)

        sections = []
        current_section_text = ""
        prev_header_level = 0
        prev_header_text = ""

        for i, part in enumerate(parts):
            # Skip empty parts or pure header lines
            if not part.strip() and (i < len(parts) - 1 and re.match(pattern, parts[i + 1].strip())):
                continue

            stripped = part.strip()

            # Check if this is a header
            match = re.match(pattern, stripped)
            if match:
                level = int(match.group(1))
                heading = match.group(2).strip()

                if current_section_text and len(current_section_text.split()) > 0:
                    sections.append({
                        "title": f"Section {heading}",
                        "text": current_section_text,
                        "level": prev_header_level
                    })

                # Start new section
                current_section_text = ""
            else:
                if current_section_text == "":
                    current_section_text = stripped + "\n"
                else:
                    current_section_text += stripped + "\n"

        # Add final section content
        if len(current_section_text.split()) > 0:
            sections.append({
                "title": f"Section {prev_header_text}",
                "text": current_section_text,
                "level": prev_header_level
            })

        return sections

    def chunk_document(
        self,
        text: str,
        max_words: int = 400,
        min_chunk_overlap_words: int = 20
    ) -> List[Chunk]:
        """Split document into chunks by Markdown headers.

        If a section exceeds max_words, fall back to sliding token windows
        with overlapping margins.

        Args:
            text: Document text
            max_words: Maximum words per chunk before splitting
            min_chunk_overlap_words: Minimum overlapping words for sliding window

        Returns:
            List of Chunk objects with rich metadata
        """
        self.chunk_counter += 1
        chunks = []

        # Extract sections from document
        sections = self.extract_sections(text)

        # Process each section into chunks
        for section in sections:
            section_text = section["text"]
            words = section_text.split()

            if len(words) == 0:
                continue

            # Check if section fits in one chunk
            if len(words) <= max_words:
                self.chunk_counter += 1
                chunks.append(Chunk(
                    chunk_id=self.chunk_counter,
                    doc_id="doc",  # Will be updated by caller
                    doc_title="policy_document",
                    section=section["title"],
                    text=section_text
                ))
            else:
                # Split section into multiple chunks using sliding window
                self._chunk_with_sliding_window(
                    chunks, words, section["title"], max_words, min_chunk_overlap_words
                )

        return chunks

    def _chunk_with_sliding_window(
        self,
        chunks: List[Chunk],
        words: List[str],
        section_title: str,
        max_words: int,
        overlap_words: int
    ):
        """Split words into chunks using sliding window with overlap.

        Args:
            chunks: List to append chunks to
            words: List of words to split
            section_title: Title for the chunk's section field
            max_words: Maximum words per chunk
            overlap_words: Number of words to overlap between chunks
        """
        step = max(1, max_words - overlap_words)
        for start_idx in range(0, len(words), step):
            chunk_words = words[start_idx:start_idx + max_words]
            if not chunk_words:
                break
            self.chunk_counter += 1
            chunks.append(Chunk(
                chunk_id=self.chunk_counter,
                doc_id="doc",
                doc_title="policy_document",
                section=section_title,
                text=" ".join(chunk_words)
            ))
            if start_idx + max_words >= len(words):
                break


    def load_policies(self) -> List[Dict[str, Any]]:
        """Load and parse all policy documents.

        Returns:
            List of dictionaries with parsed document info including chunks
        """
        docs = []

        for filename in sorted(os.listdir(self.policies_dir)):
            if not filename.endswith(('.md', '.pdf')):
                continue

            file_path = os.path.join(self.policies_dir, filename)

            # Read document
            text = self.read_document(file_path)

            # Create doc_id
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".md":
                doc_id = f"doc_md_{filename}"
            else:
                doc_id = f"doc_pdf_{filename}"

            # Extract and chunk sections
            chunks = self.chunk_document(text)

            for chunk in chunks:
                chunk.doc_id = doc_id
                chunk.doc_title = os.path.basename(filename).replace("_policy", "").replace("_guide", "")

            docs.append({
                "file_path": file_path,
                "doc_id": doc_id,
                "doc_title": os.path.basename(filename),
                "chunks": [c.to_dict() for c in chunks]
            })

        return docs


def load_and_parse_policies(policies_dir: str = "data/policies") -> List[Dict[str, Any]]:
    """Load and parse all policy documents into a flat list of chunks.

    Args:
        policies_dir: Directory containing policy files

    Returns:
        Flat list of chunk dictionaries
    """
    parser = PolicyParser(policies_dir)
    docs = parser.load_policies()

    all_chunks = []
    for doc in docs:
        all_chunks.extend(doc["chunks"])
    return all_chunks

