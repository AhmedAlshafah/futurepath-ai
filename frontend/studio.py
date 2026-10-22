from __future__ import annotations

import json
from pathlib import Path

def build_studio_html(data: dict) -> str:
    """Build testable iframe HTML, safely embedding the Python-backed catalog."""
    source_path = Path(__file__).with_name("studio.html")
    source = source_path.read_text(encoding="utf-8")
    css_path = source_path.with_name("studio.css")
    css = f"<style>\n{css_path.read_text(encoding='utf-8')}\n</style>"
    source = source.replace("<!-- STUDIO_CSS -->", css)
    payload = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    payload = (payload.replace("<", "\\u003c").replace(">", "\\u003e")
               .replace("&", "\\u0026").replace("\u2028", "\\u2028")
               .replace("\u2029", "\\u2029"))
    return source.replace("__FUTUREPATH_DATA__", payload)


def render_studio(data: dict) -> None:
    """Render studio at viewport size without Streamlit chrome or outer scroll."""
    import streamlit as st
    import streamlit.components.v1 as components

    st.markdown(
        """<style>
        [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
        [data-testid="stSidebar"],footer{display:none!important}
        .stApp{height:100dvh;overflow:hidden}
        .block-container{max-width:none!important;padding:0!important}
        [data-testid="stMainBlockContainer"]{padding:0!important}
        [data-testid="stVerticalBlock"]{gap:0!important}
        [data-testid="stAppViewContainer"],[data-testid="stMain"]{height:100dvh;overflow:hidden}
        [data-testid="stIFrame"],[data-testid="stIFrame"] iframe{height:100dvh!important;min-height:100dvh!important}
        iframe{display:block}
        </style>""",
        unsafe_allow_html=True,
    )
    components.html(build_studio_html(data), height=1000, scrolling=False)
