from observatory.coverage import classify_format


def test_classify_xhtml_and_html():
    assert classify_format("https://a.example/wp.xhtml") == "xhtml/html"
    assert classify_format("https://a.example/wp.HTML") == "xhtml/html"


def test_classify_pdf():
    assert classify_format("https://a.example/whitepaper.pdf") == "pdf"


def test_bare_domain_is_unspecified():
    assert classify_format("WWW.SKYGATETOKEN.AT") == "unspecified"


def test_query_string_does_not_confuse_extension():
    assert classify_format("https://a.example/wp.pdf?v=2") == "pdf"


def test_empty_is_none():
    assert classify_format("") == "none"
