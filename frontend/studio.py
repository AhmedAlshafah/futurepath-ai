from __future__ import annotations

import json
from pathlib import Path

_STUDIO_COMPONENT = None


def build_studio_html(data: dict) -> str:
    """Build testable iframe HTML, safely embedding the Python-backed catalog."""
    source_path = Path(__file__).with_name("studio.html")
    source = source_path.read_text(encoding="utf-8")
    css = "\n".join(
        f"<style>\n{source_path.with_name(name).read_text(encoding='utf-8')}\n</style>"
        for name in ("journey.css", "landing.css")
    )
    source = source.replace("<!-- STUDIO_CSS -->", css)
    source = source.replace(
        "<!-- STUDIO_LANDING -->",
        source_path.with_name("landing.html").read_text(encoding="utf-8"),
    )
    source = source.replace(
        "/* STUDIO_SCRIPT */",
        "\n".join(
            source_path.with_name(name).read_text(encoding="utf-8")
            for name in ("plan_print.js", "journey.js")
        ),
    )
    payload = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    payload = (payload.replace("<", "\\u003c").replace(">", "\\u003e")
               .replace("&", "\\u0026").replace("\u2028", "\\u2028")
               .replace("\u2029", "\\u2029"))
    return source.replace("__FUTUREPATH_DATA__", payload)


def render_studio(data: dict):
    """Render the studio as a bidirectional component so Python owns match scoring."""
    import streamlit as st
    import streamlit.components.v1 as components

    global _STUDIO_COMPONENT
    if _STUDIO_COMPONENT is None:
        _STUDIO_COMPONENT = components.declare_component(
            "futurepath_studio",
            path=str(Path(__file__).parent),
        )

    st.markdown(
        """<style>
        [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
        [data-testid="stSidebar"],footer{display:none!important}
        .stApp{min-height:100dvh}
        .block-container{max-width:none!important;padding:0!important}
        [data-testid="stMainBlockContainer"]{padding:0!important}
        [data-testid="stVerticalBlock"]{gap:0!important}
        [data-testid="stAppViewContainer"],[data-testid="stMain"]{min-height:100dvh}
        [data-testid="stCustomComponentV1"]{width:100%}
        iframe{display:block}
        </style>""",
        unsafe_allow_html=True,
    )
    return _STUDIO_COMPONENT(
        html=build_studio_html(data),
        key="futurepath-studio",
        default=None,
        height=1000,
    )
