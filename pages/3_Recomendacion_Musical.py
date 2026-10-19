from pathlib import Path

import streamlit as st


st.set_page_config(page_title="Recomendación Musical", layout="wide")

css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    [data-testid="stBaseButton-primary"] {
        background-color: #B23A48;
        border-color: #B23A48;
        color: #FFFFFF;
    }

    [data-testid="stBaseButton-primary"]:hover {
        background-color: #8B2635;
        border-color: #8B2635;
        color: #FFFFFF;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #B23A48;
        border-bottom: 2px solid #B23A48;
    }

    [data-testid="stTabs"] [role="tab"]:hover {
        color: #8B2635;
    }

    .music-card {
        background: #FFF5F5;
        border-left: 5px solid #B23A48;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(139, 38, 53, 0.10);
        margin: 0.5rem 0 1rem;
        padding: 1rem 1.25rem;
    }

    .music-card h3 {
        color: #8B2635;
        margin: 0 0 0.4rem;
    }

    .music-card p {
        color: #4A3336;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Recomendación Musical")

recommendation_tab, artist_tab = st.tabs(["🎧 Recomendaciones", "🎤 Artistas"])

with recommendation_tab:
    st.markdown(
        """
        <div class="music-card">
          <h3>Recomendaciones musicales</h3>
          <p>Este espacio está preparado para recomendaciones musicales.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with artist_tab:
    st.markdown(
        """
        <div class="music-card">
          <h3>Datos de artistas</h3>
          <p>La información de artistas se agregará próximamente.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.button("⬅️ Página Central", type="primary"):
    st.switch_page("app.py")
