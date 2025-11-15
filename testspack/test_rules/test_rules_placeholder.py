from app.services.analytics.rules_analyzer.rule_paceholder import RulePlaceholderWithoutLabel
from app.services.analytics.json_parser.models import DocumentModel, ElementNode


def test_input_with_only_placeholder_violation():
    rule = RulePlaceholderWithoutLabel()

    input_field = ElementNode(
        node_id="10",
        tag="input",
        placeholder="Введите имя",
        attributes={},    # нет id → нет label
        semantics=None,
        children=[],
        text=""
    )

    document = DocumentModel(info=None, root=None, elements=[input_field])

    violations = rule.check(document)

    assert len(violations) == 1
    assert violations[0].element_id == "10"


def test_input_with_aria_label_no_violation():
    rule = RulePlaceholderWithoutLabel()

    input_field = ElementNode(
        node_id="11",
        tag="input",
        placeholder="Имя",
        attributes={},
        semantics=type("s", (), {"aria_label": "Имя поля", "aria_labelledby": []})(),
        children=[],
        text=""
    )

    document = DocumentModel(info=None, root=None, elements=[input_field])

    violations = rule.check(document)

    assert len(violations) == 0
