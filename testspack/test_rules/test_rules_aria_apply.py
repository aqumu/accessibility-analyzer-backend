from app.services.analytics.rules_analyzer.rules_aria_label import RuleAriaIncorrectUsage
from app.services.analytics.json_parser.models import DocumentModel, ElementNode


def test_aria_hidden_false_on_hidden_element_violation():
    rule = RuleAriaIncorrectUsage()

    # скрытый элемент со стилем display:none
    node = ElementNode(
        node_id="30",
        tag="div",
        attributes={"aria-hidden": "false"},
        semantics=type("s", (), {
            "role": None,
            "aria_hidden": False,
            "computed": {"display": "none"}   # элемент скрыт стилем
        })(),
        children=[],
        text=""
    )

    document = DocumentModel(info=None, root=None, elements=[node])

    violations = rule.check(document)

    assert len(violations) == 1
    assert violations[0].element_id == "30"


def test_visible_element_with_aria_hidden_false_no_violation():
    rule = RuleAriaIncorrectUsage()

    node = ElementNode(
        node_id="31",
        tag="div",
        attributes={"aria-hidden": "false"},
        semantics=type("s", (), {
            "role": None,
            "aria_hidden": False,
            "computed": {"display": "block"}   # элемент видимый
        })(),
        children=[],
        text=""
    )

    document = DocumentModel(info=None, root=None, elements=[node])

    violations = rule.check(document)

    assert len(violations) == 0
