"""Policy RAG pipeline for document retrieval and search."""

import os
import re
from typing import List, Dict, Any, Optional, Iterable

import chromadb

from rag.parser import load_and_parse_policies



import hashlib

class LightweightEmbeddingFunction(chromadb.EmbeddingFunction):
    """Deterministic, zero-download embedding function for ChromaDB.
    Avoids external S3 model downloads and ONNX CPU vector instruction crashes.
    """
    def __init__(self, dim: int = 128):
        self.dim = dim

    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        embeddings = []
        for text in input:
            vec = [0.0] * self.dim
            words = re.findall(r'\b\w+\b', str(text).lower())
            for w in words:
                h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16) % self.dim
                vec[h] += 1.0
            norm = (sum(v * v for v in vec)) ** 0.5 or 1.0
            embeddings.append([float(v / norm) for v in vec])
        return embeddings

    @staticmethod
    def name() -> str:
        return "lightweight_embedding"

    def get_config(self) -> Dict[str, Any]:
        return {"dim": self.dim}

    def max_tokens(self) -> int:
        return 512


class PolicyRAG:
    """Retrieval-Augmented Generation for policy documents.

    Provides embedding-based retrieval over policy documents using ChromaDB
    for storage and a lightweight deterministic embedding function for policy-grounded answers.
    """

    POLICY_KEYWORDS = {
        "remote", "remote work", "telework", "pto", "paid time off",
        "leave", "benefits", "equipment", "security", "data", "expense",
        "travel", "policy", "vacation", "holiday", "salary", "work from home",
        "home office", "internet", "stipend", "conduct", "ethics", "onboarding",
        "professional standards"
    }

    def __init__(self, db_path: str = "data/chroma_db", policies_dir: str = None):
        """Initialize PolicyRAG with ChromaDB instance."""
        self.db_path = os.path.abspath(db_path if db_path is not None else "data/chroma_db")
        self.policies_dir = os.path.abspath(
            policies_dir if policies_dir is not None else "data/policies"
        )

        self.client = chromadb.PersistentClient(path=self.db_path)
        self.embedding_fn = LightweightEmbeddingFunction()
        self.collection_name = "policy_documents_v2"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
        )
        if self.collection.count() == 0:
            self.build_index()

    def _rewrite_query(self, query: str) -> str:
        """Normalize a user query before semantic retrieval."""
        if not query or not str(query).strip():
            return ""
        rewritten = str(query).strip()
        rewritten = re.sub(r"\s+", " ", rewritten)
        return rewritten

    def _is_policy_query(self, query: str) -> bool:
        """Return True when a question is asking about the in-corpus HR policy set."""
        if not query:
            return False
        lower = query.lower()
        if any(keyword in lower for keyword in self.POLICY_KEYWORDS):
            return True
        return False

    def build_index(self, policies_dir: str = None):
        """Build index of policy documents."""
        dir_to_use = os.path.abspath(
            policies_dir if policies_dir is not None else self.policies_dir
        )
        print(f"Building index from {dir_to_use}...")

        if not os.path.exists(dir_to_use):
            raise FileNotFoundError(f"Policy directory does not exist: {dir_to_use}")

        chunks = load_and_parse_policies(dir_to_use)

        if not chunks:
            print("No chunks found to index.")
            return 0

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            chunk_id = f"{chunk['doc_id']}_{chunk.get('chunk_id', '0')}"
            ids.append(chunk_id)
            documents.append(chunk['text'])
            metadatas.append({
                "doc_id": chunk['doc_id'],
                "doc_title": chunk['doc_title'],
                "section": chunk['section'],
            })

        batch_size = 5000
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )

        print(f"Successfully indexed {len(chunks)} chunks.")
        return len(chunks)

    def search_policies(
        self,
        query: str,
        top_k: int = 3,
        filter_by_doc: Optional[Iterable[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute vector similarity search for relevant policy snippets.

        Args:
            query: Search query string
            top_k: Number of results to return
            filter_by_doc: Optional document IDs to restrict retrieval to

        Returns:
            List of dictionaries containing doc_id, doc_title, section, snippet, and relevance_score
        """
        normalized_query = self._rewrite_query(query)
        if not normalized_query:
            return []

        query_kwargs: Dict[str, Any] = {
            "query_texts": [normalized_query],
            "n_results": max(1, top_k),
            "include": ["documents", "metadatas", "distances"],
        }

        if filter_by_doc:
            doc_ids = list(dict.fromkeys(filter_by_doc))
            if doc_ids:
                query_kwargs["where"] = {"doc_id": {"$in": doc_ids}}

        results = self.collection.query(**query_kwargs)

        search_results = []
        if results.get("ids") and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                metadata = results["metadatas"][0][i]
                snippet = results["documents"][0][i]
                distance = results["distances"][0][i]

                relevance_score = 1 / (1 + distance) if distance is not None else 0.0
                search_results.append({
                    "doc_id": metadata.get("doc_id"),
                    "doc_title": metadata.get("doc_title"),
                    "section": metadata.get("section"),
                    "snippet": snippet,
                    "relevance_score": relevance_score,
                })

        return search_results

    def _build_policy_answer(self, question: str, matches: List[Dict[str, Any]]) -> str:
        """Build a concise answer grounded in the retrieved policy evidence."""
        if not matches:
            return "I couldn’t find enough policy evidence in the corpus to answer that question confidently."

        citations = []
        for match in matches[:3]:
            doc_id = match.get("doc_id") or "unknown"
            title = match.get("doc_title") or doc_id
            section = match.get("section") or "Policy text"
            snippet = (match.get("snippet") or "").strip()
            snippet = re.sub(r"\s+---\s+", "\n\n", snippet)
            snippet = re.sub(r"\s+(#{1,3}\s+)", r"\n\n\1", snippet)
            snippet = re.sub(r"\s+-\s+", "\n- ", snippet)
            citations.append(
                f"Source: {title} ({doc_id})\n"
                f"Section: {section}\n"
                f"Guidance:\n{snippet}"
            )

        answer = (
            "Based on the policy corpus, the relevant guidance is:\n\n"
            + "\n\n".join(citations)
        )
        return answer

    def _get_multi_document_candidates(self, question: str) -> List[str]:
        """Return likely policy document IDs for compound questions spanning multiple policy areas."""
        lower = question.lower()
        candidates = []

        if any(token in lower for token in ["remote", "telework", "home office", "internet", "equipment", "stipend", "work from home"]):
            candidates.append("doc_md_remote_work_policy.md")
        if "equipment" in lower:
            candidates.append("doc_md_equipment_policy.md")
        if any(token in lower for token in ["reimbursement", "expense", "stipend", "home office", "internet"]):
            candidates.append("doc_md_expense_policy.md")
        if any(token in lower for token in ["pto", "paid time off", "vacation", "carryover", "sick leave"]):
            candidates.append("doc_md_pto_policy.md")
        if "leave" in lower:
            candidates.append("doc_md_leave_policy.md")
        if any(token in lower for token in ["benefits", "health", "dental", "vision", "401k", "wellness"]):
            candidates.append("doc_md_benefits_guide.md")
        if any(token in lower for token in ["data", "security", "vpn", "mfa", "password", "privacy"]):
            candidates.append("doc_md_data_security_policy.md")
        if any(token in lower for token in ["onboarding", "new hire"]):
            candidates.append("doc_md_onboarding_policy.md")
        if any(token in lower for token in ["holiday", "holidays"]):
            candidates.extend(["doc_md_holidays_policy.md", "doc_pdf_holidays_policy.pdf"])
        if any(token in lower for token in ["conduct", "ethics", "professional standards"]):
            candidates.append("doc_md_code_of_conduct.md")

        return list(dict.fromkeys(candidates))

    def answer_policy_question(self, question: str) -> Dict[str, Any]:
        """Answer a policy question while enforcing corpus guardrails and citations."""
        if not question or not str(question).strip():
            return {
                "status": "refuse",
                "message": "Please ask a policy-related question about MadCo HR or workplace policies.",
                "citations": [],
            }

        # Check if question is outside policy scope (simple guardrail)
        non_policy_indicators = [
            "capital", "population", "history", "geography", "math",
            "science", "technology", "sports", "entertainment", "movie",
            "book", "music", "art", "literature"
        ]

        question_lower = question.lower()
        if any(indicator in question_lower for indicator in non_policy_indicators):
            return {
                "status": "refuse",
                "message": "I can only answer questions based on MadCo policy documents. Please ask about an HR policy topic such as remote work, PTO, benefits, or expense policies.",
                "citations": [],
            }

        question_text = str(question).strip()
        if not self._is_policy_query(question_text):
            return {
                "status": "refuse",
                "message": "I can only answer questions based on MadCo policy documents. Please ask about an HR policy topic such as PTO, benefits, remote work, leave, equipment, or data security.",
                "citations": [],
            }

        matches = self.search_policies(question_text, top_k=5)
        candidates = self._get_multi_document_candidates(question_text)
        if candidates:
            per_doc_matches = []
            for candidate in candidates:
                cand_matches = self.search_policies(question_text, top_k=2, filter_by_doc=[candidate])
                per_doc_matches.extend(cand_matches)
            if per_doc_matches:
                matches = per_doc_matches + [m for m in matches if m.get("doc_id") not in {r.get("doc_id") for r in per_doc_matches}]

        if not matches:
            return {
                "status": "redirect",
                "message": "I could not find direct policy support in the corpus for that question. Please ask about a specific MadCo policy topic or a policy section.",
                "citations": [],
            }

        deduped = []
        seen = set()
        for match in matches:
            doc_id = match.get("doc_id")
            if doc_id and doc_id in seen:
                continue
            seen.add(doc_id)
            deduped.append(match)

        citations = []
        for match in deduped[:5]:
            snippet = (match.get("snippet") or "").strip().replace("\n", " ")
            snippet = snippet[:220] + ("..." if len(snippet) > 220 else "")
            citations.append({
                "doc_id": match.get("doc_id"),
                "doc_title": match.get("doc_title"),
                "section": match.get("section"),
                "snippet": snippet,
                "relevance_score": round(float(match.get("relevance_score", 0.0) or 0.0), 4),
            })

        answer = self._build_policy_answer(question_text, deduped)
        return {
            "status": "ok",
            "message": answer,
            "answer": answer,
            "citations": citations,
            "sources": [c["doc_id"] for c in citations if c.get("doc_id")],
        }


if __name__ == "__main__":
    rag = PolicyRAG()
    rag.build_index()

    query = "remote work options"
    print(f"\nTesting search for: '{query}'")
    results = rag.search_policies(query, top_k=5)

    if results:
        for i, res in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"  Title: {res['doc_title']}")
            print(f"  Section: {res['section']}")
            print(f"  Score: {res['relevance_score']:.4f}")
            print(f"  Snippet: {res['snippet'][:200]}...")
    else:
        print("No relevant policies found.")

    print("\nSample guardrail answer:")
    print(rag.answer_policy_question("What is the capital of France?"))
