import pytest
from app.services.analytics.rules_analyzer.rule_auto_start_sound import RuleMediaAutoplay
from app.services.analytics.json_parser.models import DocumentModel, ElementNode


def test_media_autoplay_with_sound_violation():
    rule = RuleMediaAutoplay()

    video = ElementNode(
        node_id="1",
        tag="video",
        attributes={"autoplay": True},   # autoplay включён
        title=None,
        children=[],
        text=""
    )

    document = DocumentModel(info=None, root=None, elements=[video])

    violations = rule.check(document)

    assert len(violations) == 1
    assert violations[0].element_id == "1"


def test_media_autoplay_muted_no_violation():
    rule = RuleMediaAutoplay()

    video = ElementNode(
        node_id="2",
        tag="video",
        attributes={"autoplay": True, "muted": True},
        title=None,
        children=[],
        text=""
    )

    document = DocumentModel(info=None, root=None, elements=[video])

    violations = rule.check(document)

    assert len(violations) == 0
