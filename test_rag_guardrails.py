import pytest

from rag.retrieval import PolicyRAG


@pytest.fixture
def rag():
    return PolicyRAG(db_path="data/chroma_db", policies_dir="data/policies")


def test_build_index_uses_default_policy_dir(rag):
    rag.build_index()
    results = rag.search_policies("remote work policy", top_k=3)

    assert len(results) > 0
    assert all("doc_id" in item for item in results)
    assert all("doc_title" in item for item in results)
    assert all("section" in item for item in results)


def test_guardrails_refuse_out_of_corpus_question(rag):
    response = rag.answer_policy_question("What is the capital of France?")

    assert response["status"] in {"refuse", "redirect"}
    assert "policy" in response["message"].lower()


def test_multi_document_question_yields_citations(rag):
    response = rag.answer_policy_question(
        "What remote-work equipment stipend and internet reimbursement are available?"
    )

    assert response["status"] == "ok"
    assert len(response["citations"]) >= 2
    cited_docs = {citation["doc_id"] for citation in response["citations"]}
    assert any("remote_work_policy" in doc for doc in cited_docs)
    assert any("expense_policy" in doc for doc in cited_docs)
