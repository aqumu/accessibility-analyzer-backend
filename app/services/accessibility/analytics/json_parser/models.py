from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


# ---------------------------
# Document level information
# ---------------------------
@dataclass
class DocumentInfo:
    title: str
    lang: str
    parse_errors: List[str]


# ---------------------------
# Base DOM Node Interface
# ---------------------------
class BaseNode(Protocol):
    tag: str
    children: List["ElementNode"]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "BaseNode":
        ...


# ---------------------------
# Strongly typed substructures
# ---------------------------

@dataclass
class MediaInfo:
    """Information about media elements (img, video, audio)."""
    alt: Optional[str] = None
    src: Optional[str] = None
    title: Optional[str] = None


@dataclass
class NodeStyles:
    color: Optional[str] = None
    backgroundColor: Optional[str] = None
    fontSize: Optional[str] = None


@dataclass
class NodeSemantics:
    role: Optional[str] = None
    implicit_role: Optional[str] = None
    aria_label: Optional[str] = None
    aria_labelledby: List[str] = field(default_factory=list)
    aria_describedby: List[str] = field(default_factory=list)
    aria_hidden: Optional[bool] = False
    accessible_name: Optional[str] = None


@dataclass
class NodeInteraction:
    focusable: Optional[bool] = False
    programmable_focusable: Optional[bool] = False
    tabindex: Optional[int] = None
    has_click_handler: Optional[bool] = False
    has_key_handler: Optional[bool] = False


@dataclass
class NodeLayout:
    order_dom: Optional[int] = None
    order_visual: Optional[int] = None
    position: Optional[str] = None
    coordinates: Optional[Dict[str, int]] = None


@dataclass
class FormInfo:
    type: Optional[str] = None
    required: Optional[bool] = None
    label: Optional[str] = None
    label_for: Optional[str] = None
    described_by: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)


# ---------------------------
# Main DOM element
# ---------------------------
@dataclass
class ElementNode:
    tag: str

    # raw HTML attributes
    attributes: Dict[str, Any] = field(default_factory=dict)

    # CSS & computed layout
    styles: Dict[str, Any] = field(default_factory=dict)
    computed: Dict[str, Any] = field(default_factory=dict)
    pseudo: Dict[str, Any] = field(default_factory=dict)

    # semantic accessibility layers
    semantics: Optional[NodeSemantics] = None
    interaction: Optional[NodeInteraction] = None
    layout: Optional[NodeLayout] = None
    form: Optional[FormInfo] = None

    # media information (img/video/audio)
    media: Optional[MediaInfo] = None

    # raw textual content
    text: Optional[str] = None

    dom_path: Optional[str] = None

    # children
    children: List["ElementNode"] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ElementNode":
        """Convert a JSON element into ElementNode with all nested structures."""

        # Parse optional subschemas
        semantics = NodeSemantics(**data.get("semantics", {})) if "semantics" in data else None
        interaction = NodeInteraction(**data.get("interaction", {})) if "interaction" in data else None
        layout = NodeLayout(**data.get("layout", {})) if "layout" in data else None
        form = FormInfo(**data.get("form", {})) if "form" in data else None

        # ---- MEDIA SECTION ----
        media = None
        if data["tag"] == "img":
            media = MediaInfo(
                alt=data.get("attributes", {}).get("alt"),
                src=data.get("attributes", {}).get("src"),
                title=data.get("attributes", {}).get("title"),
            )

        # Parse children
        children = [
            ElementNode.from_json(child)
            for child in data.get("children", [])
        ]

        return cls(
            tag=data["tag"],
            attributes=data.get("attributes", {}),
            styles=data.get("styles", {}),
            computed=data.get("computed", {}),
            pseudo=data.get("pseudo", {}),
            semantics=semantics,
            interaction=interaction,
            layout=layout,
            form=form,
            media=media,
            text=data.get("text"),
            dom_path=data.get("dom_path"),
            children=children
        )


# ---------------------------
# Full document
# ---------------------------
@dataclass
class DocumentModel:
    info: DocumentInfo
    root: ElementNode


# ---------------------------
# Factory for building the document
# ---------------------------
class DocumentFactory:
    @staticmethod
    def load_from_json(data: Dict[str, Any]) -> DocumentModel:
        """
        Expected JSON format:
        {
            "document": {
                "title": "...",
                "lang": "...",
                "parse_errors": []
            },
            "dom": { ElementNode JSON }
        }
        """
        doc_info = DocumentInfo(
            title=data["document"]["title"],
            lang=data["document"]["lang"],
            parse_errors=data["document"].get("parse_errors", [])
        )

        root_node = ElementNode.from_json(data["dom"])

        return DocumentModel(info=doc_info, root=root_node)
