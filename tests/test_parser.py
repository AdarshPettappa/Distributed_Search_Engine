from search_engine.models import RawDocument
from search_engine.parser import parse_document


def test_parser_extracts_title_text_and_links():
    raw = RawDocument(
        doc_id="doc1",
        source_path="memory",
        html="""
        <html><head><title>Example Page</title></head>
        <body><script>ignored()</script><p>Hello <a href="Target_Page.html">target</a></p></body></html>
        """,
    )

    parsed = parse_document(raw)

    assert parsed.title == "Example Page"
    assert "Hello target" in parsed.text
    assert "ignored" not in parsed.text
    assert parsed.links == ["target_page"]
