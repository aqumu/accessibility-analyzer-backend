from app.services.analytics.rules_analyzer.rule_tables_sh import RuleTableNoHeaders
from app.services.analytics.json_parser.models import DocumentModel, ElementNode


def test_table_without_th_violation():
    rule = RuleTableNoHeaders()

    table = ElementNode(
        node_id="20",
        tag="table",
        attributes={},
        children=[
            ElementNode(node_id="21", tag="tr", attributes={}, children=[], text="")
        ],
        text=""
    )

    document = DocumentModel(info=None, root=None, elements=[table])

    violations = rule.check(document)

    assert len(violations) == 1
    assert violations[0].element_id == "20"


def test_table_with_th_no_violation():
    rule = RuleTableNoHeaders()

    table = ElementNode(
        node_id="22",
        tag="table",
        attributes={},
        children=[
            ElementNode(
                node_id="23",
                tag="th",
                attributes={},
                children=[],
                text="Заголовок"
            )
        ],
        text=""
    )

    document = DocumentModel(info=None, root=None, elements=[table])

    violations = rule.check(document)

    assert len(violations) == 0
