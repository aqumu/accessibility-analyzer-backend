from .aria_analyzer import AriaAnalyzer
from .alt_analyzer import AltAnalyzer
from .role_analyzer import RoleAnalyzer
from .css_analyzer import CssAnalyzer
from .text_analyzer import TextAnalyzer
from .visibility_analyzer import VisibilityAnalyzer
from .link_analyzer import LinkAnalyzer

ANALYZERS = [
    AriaAnalyzer(),
    AltAnalyzer(),
    RoleAnalyzer(),
    CssAnalyzer(),
    TextAnalyzer(),
    VisibilityAnalyzer(),
    LinkAnalyzer(),
]
